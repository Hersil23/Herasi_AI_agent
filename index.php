<?php
// index.php - Bot de WhatsApp con IA usando DeepSeek
header('Content-Type: application/json');

// Cargar variables de entorno
$DEEPSEEK_API_KEY = getenv('DEEPSEEK_API_KEY');
$WAMUNDO_API_KEY = getenv('WAMUNDO_API_KEY');
$WAMUNDO_PHONE_ID = getenv('WAMUNDO_PHONE_ID');

// Si no están en el entorno, intentar cargar desde .env
if (!$DEEPSEEK_API_KEY || !$WAMUNDO_API_KEY || !$WAMUNDO_PHONE_ID) {
    if (file_exists(__DIR__ . '/.env')) {
        $env = parse_ini_file(__DIR__ . '/.env');
        $DEEPSEEK_API_KEY = $env['DEEPSEEK_API_KEY'] ?? '';
        $WAMUNDO_API_KEY = $env['WAMUNDO_API_KEY'] ?? '';
        $WAMUNDO_PHONE_ID = $env['WAMUNDO_PHONE_ID'] ?? '';
    }
}

// Función para consultar DeepSeek
function consultarDeepSeek($mensajeUsuario) {
    global $DEEPSEEK_API_KEY;
    
    $url = "https://api.deepseek.com/chat/completions";
    
    $data = [
        "model" => "deepseek-chat",
        "messages" => [
            [
                "role" => "system",
                "content" => "Eres Herasi AI Agent, un asistente virtual inteligente y amigable. Ayudas a los usuarios con sus consultas de manera clara, concisa y útil. Siempre respondes en el idioma del usuario."
            ],
            [
                "role" => "user",
                "content" => $mensajeUsuario
            ]
        ],
        "temperature" => 0.7,
        "max_tokens" => 500
    ];
    
    $options = [
        'http' => [
            'method' => 'POST',
            'header' => [
                "Content-Type: application/json",
                "Authorization: Bearer " . $DEEPSEEK_API_KEY
            ],
            'content' => json_encode($data),
            'timeout' => 30
        ]
    ];
    
    $context = stream_context_create($options);
    $response = @file_get_contents($url, false, $context);
    
    if ($response === false) {
        error_log("Error al consultar DeepSeek API");
        return "Lo siento, hubo un error al procesar tu mensaje. Por favor intenta de nuevo.";
    }
    
    $result = json_decode($response, true);
    
    if (isset($result['choices'][0]['message']['content'])) {
        return $result['choices'][0]['message']['content'];
    }
    
    return "Lo siento, no pude procesar tu mensaje en este momento.";
}

// Función para enviar mensaje por WhatsApp
function enviarMensajeWhatsApp($numeroDestino, $mensaje) {
    global $WAMUNDO_API_KEY, $WAMUNDO_PHONE_ID;
    
    $url = "https://api.wamundo.com/send-message";
    
    $data = [
        "phone_id" => $WAMUNDO_PHONE_ID,
        "to" => $numeroDestino,
        "message" => $mensaje
    ];
    
    $options = [
        'http' => [
            'method' => 'POST',
            'header' => [
                "Content-Type: application/json",
                "Authorization: Bearer " . $WAMUNDO_API_KEY
            ],
            'content' => json_encode($data),
            'timeout' => 30
        ]
    ];
    
    $context = stream_context_create($options);
    $response = @file_get_contents($url, false, $context);
    
    if ($response === false) {
        error_log("Error al enviar mensaje por WhatsApp");
        return false;
    }
    
    return true;
}

// Obtener el método HTTP
$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

// Endpoint raíz - verificar status
if ($path === '/bot/' || $path === '/bot' || $path === '/bot/index.php') {
    if ($method === 'GET') {
        echo json_encode([
            "status" => "online",
            "bot" => "Herasi AI Agent",
            "message" => "Bot de WhatsApp con IA funcionando correctamente"
        ]);
        exit;
    }
}

// Endpoint webhook - recibir mensajes de WaMundo
if ($path === '/bot/webhook' || $path === '/bot/webhook.php') {
    if ($method === 'POST') {
        // Obtener datos del webhook
        $input = file_get_contents('php://input');
        $data = json_decode($input, true);
        
        // Log para debugging
        error_log("Webhook recibido: " . $input);
        
        if (isset($data['from']) && isset($data['message']['body'])) {
            $numeroRemitente = $data['from'];
            $mensajeRecibido = $data['message']['body'];
            
            // Consultar IA
            $respuestaIA = consultarDeepSeek($mensajeRecibido);
            
            // Enviar respuesta por WhatsApp
            enviarMensajeWhatsApp($numeroRemitente, $respuestaIA);
            
            echo json_encode([
                "status" => "success",
                "message" => "Mensaje procesado correctamente"
            ]);
        } else {
            http_response_code(400);
            echo json_encode([
                "status" => "error",
                "message" => "Formato de mensaje inválido"
            ]);
        }
        exit;
    }
}

// Endpoint de prueba
if ($path === '/bot/test' || $path === '/bot/test.php') {
    if ($method === 'POST') {
        $input = file_get_contents('php://input');
        $data = json_decode($input, true);
        
        if (isset($data['mensaje'])) {
            $respuesta = consultarDeepSeek($data['mensaje']);
            echo json_encode([
                "status" => "success",
                "respuesta" => $respuesta
            ]);
        } else {
            http_response_code(400);
            echo json_encode([
                "status" => "error",
                "message" => "Falta el parámetro 'mensaje'"
            ]);
        }
        exit;
    }
}

// Si no coincide con ninguna ruta
http_response_code(404);
echo json_encode([
    "status" => "error",
    "message" => "Endpoint no encontrado"
]);
?>