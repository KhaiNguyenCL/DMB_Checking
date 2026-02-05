<?php

/**
 * Test Bitrix24 CRM Products API
 * Get products data from Bitrix24 Catalog
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

    \Bitrix\Main\Loader::includeModule('catalog');
    \Bitrix\Main\Loader::includeModule('iblock');
    \Bitrix\Main\Loader::includeModule('crm');

    $action = isset($_GET['action']) ? $_GET['action'] : 'list';
    $startTime = microtime(true);

    if ($action === 'fields') {
        // Get product fields description
        $fieldsData = [];

        // Get catalog IBlocks
        $catalogs = \CCrmCatalog::GetList();
        $catalogIBlocks = [];
        while ($catalog = $catalogs->Fetch()) {
            $catalogIBlocks[] = [
                'ID' => $catalog['IBLOCK_ID'],
                'NAME' => $catalog['NAME'],
                'TYPE_ID' => $catalog['IBLOCK_TYPE_ID']
            ];
        }

        // Get fields for first catalog (if exists)
        if (!empty($catalogIBlocks)) {
            $iblockId = $catalogIBlocks[0]['ID'];

            // Get IBlock properties
            $properties = CIBlockProperty::GetList(
                ['SORT' => 'ASC'],
                ['IBLOCK_ID' => $iblockId, 'ACTIVE' => 'Y']
            );

            while ($prop = $properties->Fetch()) {
                $fieldsData[$prop['CODE']] = [
                    'name' => $prop['CODE'],
                    'title' => $prop['NAME'],
                    'type' => $prop['PROPERTY_TYPE'],
                    'multiple' => $prop['MULTIPLE'] === 'Y',
                    'required' => $prop['IS_REQUIRED'] === 'Y'
                ];
            }
        }

        ob_end_clean();
        echo json_encode([
            'success' => true,
            'data' => [
                'catalogs' => $catalogIBlocks,
                'fields' => $fieldsData
            ],
            'total' => count($fieldsData),
            'execution_time' => round(microtime(true) - $startTime, 3) . 's'
        ], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        exit;
    }

    // Get list of products
    $count = isset($_GET['count']) ? intval($_GET['count']) : 50;

    // Get all catalog IBlocks
    $catalogs = \CCrmCatalog::GetList();
    $allProducts = [];

    while ($catalog = $catalogs->Fetch()) {
        $iblockId = $catalog['IBLOCK_ID'];

        // Get products from this catalog
        $result = CIBlockElement::GetList(
            ['ID' => 'DESC'],
            [
                'IBLOCK_ID' => $iblockId,
                'ACTIVE' => 'Y'
            ],
            false,
            ['nTopCount' => $count],
            ['ID', 'NAME', 'IBLOCK_ID', 'IBLOCK_NAME', 'DETAIL_TEXT', 'PREVIEW_TEXT']
        );

        while ($product = $result->Fetch()) {
            // Get product properties
            $properties = [];
            $propResult = CIBlockElement::GetProperty(
                $iblockId,
                $product['ID'],
                ['sort' => 'asc'],
                []
            );

            while ($prop = $propResult->Fetch()) {
                if (!empty($prop['VALUE'])) {
                    $properties[$prop['CODE']] = [
                        'name' => $prop['NAME'],
                        'value' => $prop['VALUE'],
                        'type' => $prop['PROPERTY_TYPE']
                    ];
                }
            }

            // Get price
            $price = \CCatalogProduct::GetByID($product['ID']);

            $allProducts[] = [
                'id' => $product['ID'],
                'name' => $product['NAME'],
                'iblock_id' => $product['IBLOCK_ID'],
                'iblock_name' => $product['IBLOCK_NAME'],
                'description' => $product['DETAIL_TEXT'],
                'preview' => $product['PREVIEW_TEXT'],
                'price' => $price,
                'properties' => $properties
            ];
        }
    }

    ob_end_clean();

    echo json_encode([
        'success' => true,
        'data' => $allProducts,
        'total' => count($allProducts),
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
