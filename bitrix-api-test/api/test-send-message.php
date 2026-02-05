<?php

/**
 * Test Bitrix24 IM API - Send Message
 * Send message to a chat or group
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

    // Get POST data
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if (!$data) {
        // Try to get from $_POST
        $data = $_POST;
    }

    // Validate input
    if (empty($data['chat_id'])) {
        throw new Exception('Chat ID is required');
    }

    if (empty($data['message'])) {
        throw new Exception('Message is required');
    }

    $chatId = intval($data['chat_id']);
    $message = $data['message'];
    $systemMessage = isset($data['system']) && $data['system'] === true ? 'Y' : 'N';

    // Optional: mentions
    $mentions = [];
    if (!empty($data['mentions']) && is_array($data['mentions'])) {
        foreach ($data['mentions'] as $userId) {
            $mentions[] = intval($userId);
        }
    }

    // Prepare message with mentions
    if (!empty($mentions)) {
        $mentionText = '';
        foreach ($mentions as $userId) {
            $mentionText .= "[USER={$userId}][/USER] ";
        }
        $message = $mentionText . $message;
    }

    // Send message
    $messageId = \CIMMessenger::Add([
        'MESSAGE_TYPE' => \IM_MESSAGE_CHAT,
        'TO_CHAT_ID' => $chatId,
        'FROM_USER_ID' => $USER->GetID(),
        'MESSAGE' => $message,
        'SYSTEM' => $systemMessage
    ]);

    if (!$messageId) {
        global $APPLICATION;
        $error = $APPLICATION->GetException();
        throw new Exception($error ? $error->GetString() : 'Failed to send message');
    }

    // Get sent message info
    $sentMessage = \Bitrix\Im\Model\MessageTable::getById($messageId)->fetch();

    // Clean all output and send JSON
    $output = ob_get_clean();

    echo json_encode([
        'success' => true,
        'message_id' => $messageId,
        'chat_id' => $chatId,
        'message' => $message,
        'sent_at' => $sentMessage ? $sentMessage['DATE_CREATE']->toString() : date('Y-m-d H:i:s'),
        'execution_time' => round(microtime(true) - $startTime, 3) . 's'
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

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
