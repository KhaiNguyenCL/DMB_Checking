<?php

/**
 * Test Bitrix24 IM API - Get Chat List
 * Get list of all chats and groups
 */

// Start output buffering immediately
while (ob_get_level()) {
    ob_end_clean();
}
ob_start();

header('Content-Type: application/json; charset=utf-8');

define('NO_KEEP_STATISTIC', true);
define('NOT_CHECK_PERMISSIONS', false);
define('NO_AGENT_CHECK', true);

try {
    require($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php');

    // Clean all output buffers from Bitrix
    while (ob_get_level() > 1) {
        ob_end_clean();
    }

    global $USER;
    if (!$USER->IsAuthorized()) {
        throw new Exception('Unauthorized - Please login to Bitrix24', 401);
    }

    if (!\Bitrix\Main\Loader::includeModule('im')) {
        throw new Exception('IM module is not installed or not available');
    }

    $startTime = microtime(true);
    $userId = $USER->GetID();

    // Get limit from query params (default 100, max 500)
    $limit = isset($_GET['limit']) ? intval($_GET['limit']) : 100;
    $limit = min(max($limit, 1), 500); // Clamp between 1 and 500

    $chatList = [];
    $totalChatsScanned = 0;
    $totalChatsFound = 0;

    // Get all chats using ChatTable directly
    $chatsResult = \Bitrix\Im\Model\ChatTable::getList([
        'select' => ['ID', 'TYPE', 'ENTITY_TYPE', 'ENTITY_ID', 'TITLE', 'DESCRIPTION', 'AUTHOR_ID', 'AVATAR', 'COLOR', 'MESSAGE_COUNT', 'DATE_CREATE'],
        'order' => ['MESSAGE_COUNT' => 'DESC'],
        'limit' => $limit
    ]);

    while ($chat = $chatsResult->fetch()) {
        $totalChatsScanned++;

        // Check if user is a member of this chat
        $isMember = \Bitrix\Im\Model\RelationTable::getCount([
            'CHAT_ID' => $chat['ID'],
            'USER_ID' => $userId
        ]);

        if (!$isMember) {
            continue; // Skip chats where user is not a member
        }

        $totalChatsFound++;

        // Get chat users count
        $userCount = \Bitrix\Im\Model\RelationTable::getCount([
            'CHAT_ID' => $chat['ID']
        ]);

        // Get users in this chat (limit to first 10)
        $relations = \Bitrix\Im\Model\RelationTable::getList([
            'filter' => ['CHAT_ID' => $chat['ID']],
            'select' => ['USER_ID'],
            'limit' => 10
        ])->fetchAll();

        $users = [];
        foreach ($relations as $rel) {
            $user = \CUser::GetByID($rel['USER_ID'])->Fetch();
            if ($user) {
                $users[] = [
                    'id' => $user['ID'],
                    'name' => trim($user['NAME'] . ' ' . $user['LAST_NAME'])
                ];
            }
        }

        $chatList[] = [
            'id' => intval($chat['ID']),
            'type' => $chat['TYPE'], // P=private, O=open, C=call, etc
            'entity_type' => $chat['ENTITY_TYPE'] ?? '',
            'entity_id' => $chat['ENTITY_ID'] ?? '',
            'title' => $chat['TITLE'] ?? 'Untitled Chat',
            'description' => $chat['DESCRIPTION'] ?? '',
            'author_id' => intval($chat['AUTHOR_ID']),
            'color' => $chat['COLOR'] ?? '',
            'message_count' => intval($chat['MESSAGE_COUNT'] ?? 0),
            'user_count' => $userCount,
            'date_create' => $chat['DATE_CREATE'] ? $chat['DATE_CREATE']->toString() : '',
            'users' => $users
        ];
    }

    // Clean all output and send JSON
    $output = ob_get_clean();

    $response = [
        'success' => true,
        'data' => $chatList,
        'total' => count($chatList),
        'current_user_id' => $userId,
        'debug' => [
            'total_chats_scanned' => $totalChatsScanned,
            'total_chats_where_user_is_member' => $totalChatsFound,
            'limit_used' => $limit,
            'note' => 'Only showing chats where you are a member. Use ?limit=N to increase scan limit (max 500)'
        ],
        'execution_time' => round(microtime(true) - $startTime, 3) . 's'
    ];

    echo json_encode($response, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

} catch (Exception $e) {
    // Clean all output buffers
    while (ob_get_level()) {
        ob_end_clean();
    }

    http_response_code($e->getCode() ?: 400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'file' => $e->getFile(),
        'line' => $e->getLine()
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
}

exit;
