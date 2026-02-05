<?php

/**
 * Test Bitrix24 CRM Activities API
 * Get activities data from Bitrix24 CRM (calls, meetings, emails, etc.)
 */

header('Content-Type: application/json; charset=utf-8');

define('NO_KEEP_STATISTIC', true);
define('NOT_CHECK_PERMISSIONS', false);
define('NO_AGENT_CHECK', true);

ob_start();

try {
    require($_SERVER['DOCUMENT_ROOT'] . '/bitrix/modules/main/include/prolog_before.php');
    ob_end_clean();
    ob_start();

    global $USER;
    if (!$USER->IsAuthorized()) {
        throw new Exception('Unauthorized', 401);
    }

    \Bitrix\Main\Loader::includeModule('crm');

    $action = isset($_GET['action']) ? $_GET['action'] : 'list';
    $startTime = microtime(true);

    if ($action === 'fields') {
        // Get all fields description
        $fields = \Bitrix\Crm\ActivityTable::getMap();
        $fieldsData = [];

        foreach ($fields as $field) {
            $fieldsData[$field->getName()] = [
                'name' => $field->getName(),
                'type' => get_class($field),
                'title' => $field->getTitle() ?: $field->getName()
            ];
        }

        // Get activity types
        $activityTypes = [
            \CCrmActivityType::Meeting => 'Meeting',
            \CCrmActivityType::Call => 'Call',
            \CCrmActivityType::Email => 'Email',
            \CCrmActivityType::Task => 'Task',
            \CCrmActivityType::Provider => 'Provider'
        ];

        ob_end_clean();
        echo json_encode([
            'success' => true,
            'data' => [
                'fields' => $fieldsData,
                'activity_types' => $activityTypes
            ],
            'total' => count($fieldsData),
            'execution_time' => round(microtime(true) - $startTime, 3) . 's'
        ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        exit;
    }

    // Get list of activities
    $count = isset($_GET['count']) ? intval($_GET['count']) : 50;

    $activities = \Bitrix\Crm\ActivityTable::getList([
        'select' => ['*'],
        'order' => ['ID' => 'DESC'],
        'limit' => $count
    ])->fetchAll();

    // Add type names
    foreach ($activities as &$activity) {
        $typeId = $activity['TYPE_ID'];
        $activity['TYPE_NAME'] = [
            \CCrmActivityType::Meeting => 'Meeting',
            \CCrmActivityType::Call => 'Call',
            \CCrmActivityType::Email => 'Email',
            \CCrmActivityType::Task => 'Task',
            \CCrmActivityType::Provider => 'Provider'
        ][$typeId] ?? 'Unknown';

        // Get bindings (which entity this activity is linked to)
        $bindings = \Bitrix\Crm\ActivityBindingTable::getList([
            'filter' => ['ACTIVITY_ID' => $activity['ID']],
            'select' => ['OWNER_TYPE_ID', 'OWNER_ID']
        ])->fetchAll();

        $activity['BINDINGS'] = $bindings;
    }

    ob_end_clean();

    echo json_encode([
        'success' => true,
        'data' => $activities,
        'total' => count($activities),
        'execution_time' => round(microtime(true) - $startTime, 3) . 's'
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

} catch (Exception $e) {
    @ob_end_clean();
    http_response_code($e->getCode() ?: 400);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage(),
        'trace' => $e->getTraceAsString()
    ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
}

exit;
