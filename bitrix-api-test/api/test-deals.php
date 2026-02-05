<?php

/**
 * Test Bitrix24 CRM Deals API
 * Get deals data from Bitrix24 CRM
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
        $fields = \Bitrix\Crm\DealTable::getMap();
        $fieldsData = [];

        foreach ($fields as $field) {
            $fieldsData[$field->getName()] = [
                'name' => $field->getName(),
                'type' => get_class($field),
                'title' => $field->getTitle() ?: $field->getName()
            ];
        }

        // Also get user fields
        $userFields = $GLOBALS['USER_FIELD_MANAGER']->GetUserFields('CRM_DEAL');
        foreach ($userFields as $field) {
            $fieldsData[$field['FIELD_NAME']] = [
                'name' => $field['FIELD_NAME'],
                'type' => $field['USER_TYPE']['USER_TYPE_ID'],
                'title' => $field['EDIT_FORM_LABEL'],
                'mandatory' => $field['MANDATORY'] === 'Y',
                'multiple' => $field['MULTIPLE'] === 'Y'
            ];
        }

        ob_end_clean();
        echo json_encode([
            'success' => true,
            'data' => $fieldsData,
            'total' => count($fieldsData),
            'execution_time' => round(microtime(true) - $startTime, 3) . 's'
        ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        exit;
    }

    // Get list of deals
    $count = isset($_GET['count']) ? intval($_GET['count']) : 50;

    $deals = \Bitrix\Crm\DealTable::getList([
        'select' => ['*'],
        'order' => ['ID' => 'DESC'],
        'limit' => $count
    ])->fetchAll();

    // Get user fields and products for each deal
    foreach ($deals as &$deal) {
        // Get user fields
        $userFields = $GLOBALS['USER_FIELD_MANAGER']->GetUserFields('CRM_DEAL', $deal['ID']);
        foreach ($userFields as $field) {
            if (!empty($field['VALUE'])) {
                $deal[$field['FIELD_NAME']] = $field['VALUE'];
            }
        }

        // Get deal products
        $productRows = \CCrmDeal::LoadProductRows($deal['ID']);
        $deal['PRODUCTS'] = $productRows;
    }

    ob_end_clean();

    echo json_encode([
        'success' => true,
        'data' => $deals,
        'total' => count($deals),
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
