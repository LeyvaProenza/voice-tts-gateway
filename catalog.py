"""
Catálogo Curado de Voces Educativas para Voice-TTS Gateway.
Define las voces disponibles para Edge-TTS, Kokoro-82M y Xiaomi MiMo v2.5.
"""

from typing import Dict, List, Any

VOICES_CATALOG: Dict[str, List[Dict[str, Any]]] = {
    "es": [
        # --- RECOMENDADAS PARA DOCENCIA (MICROSOFT EDGE NEURAL) ---
        {
            "id": "es-MX-JorgeNeural",
            "name": "Jorge (Recomendado)",
            "gender": "Masculino",
            "accent": "México",
            "category": "⭐ Recomendadas Docencia (Edge Neural)",
            "recommended": True,
            "description": "Tono sereno, cálido y explicativo. Máxima naturalidad y dicción impecable para docencia y tutoriales.",
            "engine": "edge-tts"
        },
        {
            "id": "es-MX-DaliaNeural",
            "name": "Dalia (Recomendada)",
            "gender": "Femenino",
            "accent": "México",
            "category": "⭐ Recomendadas Docencia (Edge Neural)",
            "recommended": True,
            "description": "Voz clara, empática y natural, excelente para exposiciones y material formativo.",
            "engine": "edge-tts"
        },
        # --- KOKORO AI ESPAÑOL Y MEZCLAS (EXPERIMENTAL EN GPU) ---
        {
            "id": "ef_dora,af_sarah",
            "name": "Dora & Sarah (Mezcla Educativa)",
            "gender": "Femenino",
            "accent": "Hispano-American Blend",
            "category": "Kokoro AI Español (Experimental GPU)",
            "recommended": False,
            "description": "Pronunciación en español de Dora con la cadencia de Sarah. Procesado en GPU.",
            "engine": "kokoro"
        },
        {
            "id": "ef_dora,af_bella",
            "name": "Dora & Bella (Mezcla Dinámica)",
            "gender": "Femenino",
            "accent": "Hispano-American Blend",
            "category": "Kokoro AI Español (Experimental GPU)",
            "recommended": False,
            "description": "Dicción viva con consonantes claras para explicaciones paso a paso.",
            "engine": "kokoro"
        },
        {
            "id": "ef_dora,em_alex",
            "name": "Dora & Alex (Mezcla Dual)",
            "gender": "Híbrido",
            "accent": "Hispano Blend",
            "category": "Kokoro AI Español (Experimental GPU)",
            "recommended": False,
            "description": "Fusión de tonos femenino y masculino nativos en español.",
            "engine": "kokoro"
        },
        {
            "id": "ef_dora",
            "name": "Dora (Kokoro GPU)",
            "gender": "Femenino",
            "accent": "Español",
            "category": "Kokoro AI Español (Experimental GPU)",
            "recommended": False,
            "description": "Voz femenina nativa de Kokoro en español ejecutada en local en tu GPU.",
            "engine": "kokoro"
        },
        {
            "id": "em_alex",
            "name": "Alex (Kokoro GPU)",
            "gender": "Masculino",
            "accent": "Español",
            "category": "Kokoro AI Español (Experimental GPU)",
            "recommended": False,
            "description": "Voz masculina nativa de Kokoro en español ejecutada en GPU.",
            "engine": "kokoro"
        },
        {
            "id": "es-CO-GonzaloNeural",
            "name": "Gonzalo",
            "gender": "Masculino",
            "accent": "Colombia",
            "category": "Colombia (Edge Neural)",
            "recommended": False,
            "description": "Acento neutro y formal, ideal para lecturas académicas o científicas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CO-SalomeNeural",
            "name": "Salomé",
            "gender": "Femenino",
            "accent": "Colombia",
            "category": "Colombia (Edge Neural)",
            "recommended": False,
            "description": "Tono pausado y suave, muy adecuado para audiolibros educativos.",
            "engine": "edge-tts"
        },
        {
            "id": "es-PE-AlexNeural",
            "name": "Alex",
            "gender": "Masculino",
            "accent": "Perú",
            "category": "Perú (Edge Neural)",
            "recommended": False,
            "description": "Locución clara, pausada y con acento andino formal.",
            "engine": "edge-tts"
        },
        {
            "id": "es-PE-CamilaNeural",
            "name": "Camila",
            "gender": "Femenino",
            "accent": "Perú",
            "category": "Perú (Edge Neural)",
            "recommended": False,
            "description": "Tono empático, suave y de excelente articulación.",
            "engine": "edge-tts"
        },
        {
            "id": "es-AR-TomasNeural",
            "name": "Tomás",
            "gender": "Masculino",
            "accent": "Argentina",
            "category": "Argentina (Edge Neural)",
            "recommended": False,
            "description": "Locución segura, moderna y profesional.",
            "engine": "edge-tts"
        },
        {
            "id": "es-AR-ElenaNeural",
            "name": "Elena",
            "gender": "Femenino",
            "accent": "Argentina",
            "category": "Argentina (Edge Neural)",
            "recommended": False,
            "description": "Voz expresiva, viva y clara.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CL-LorenzoNeural",
            "name": "Lorenzo",
            "gender": "Masculino",
            "accent": "Chile",
            "category": "Chile (Edge Neural)",
            "recommended": False,
            "description": "Locución sobria y formal.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CL-CatalinaNeural",
            "name": "Catalina",
            "gender": "Femenino",
            "accent": "Chile",
            "category": "Chile (Edge Neural)",
            "recommended": False,
            "description": "Voz limpia, expresiva y didáctica.",
            "engine": "edge-tts"
        },
        {
            "id": "es-VE-SebastianNeural",
            "name": "Sebastián",
            "gender": "Masculino",
            "accent": "Venezuela",
            "category": "Venezuela (Edge Neural)",
            "recommended": False,
            "description": "Tono cálido, amigable y fluido.",
            "engine": "edge-tts"
        },
        {
            "id": "es-VE-PaolaNeural",
            "name": "Paola",
            "gender": "Femenino",
            "accent": "Venezuela",
            "category": "Venezuela (Edge Neural)",
            "recommended": False,
            "description": "Voz fresca, cercana y entusiasta.",
            "engine": "edge-tts"
        },
        {
            "id": "es-EC-LuisNeural",
            "name": "Luis",
            "gender": "Masculino",
            "accent": "Ecuador",
            "category": "Ecuador y Región Andina",
            "recommended": False,
            "description": "Dicción limpia y neutral.",
            "engine": "edge-tts"
        },
        {
            "id": "es-EC-AndreaNeural",
            "name": "Andrea",
            "gender": "Femenino",
            "accent": "Ecuador",
            "category": "Ecuador y Región Andina",
            "recommended": False,
            "description": "Tono educativo sereno y paciente.",
            "engine": "edge-tts"
        },
        {
            "id": "es-UY-MateoNeural",
            "name": "Mateo",
            "gender": "Masculino",
            "accent": "Uruguay",
            "category": "Uruguay (Edge Neural)",
            "recommended": False,
            "description": "Locución ríoplatense sobria y precisa.",
            "engine": "edge-tts"
        },
        {
            "id": "es-UY-ValentinaNeural",
            "name": "Valentina",
            "gender": "Femenino",
            "accent": "Uruguay",
            "category": "Uruguay (Edge Neural)",
            "recommended": False,
            "description": "Tono ameno, claro y reflexivo.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CR-JuanNeural",
            "name": "Juan",
            "gender": "Masculino",
            "accent": "Costa Rica",
            "category": "Centroamérica y Caribe",
            "recommended": False,
            "description": "Acento centroamericano neutro y pausado.",
            "engine": "edge-tts"
        },
        {
            "id": "es-CR-MariaNeural",
            "name": "María",
            "gender": "Femenino",
            "accent": "Costa Rica",
            "category": "Centroamérica y Caribe",
            "recommended": False,
            "description": "Tono dulce, claro y didáctico.",
            "engine": "edge-tts"
        },
        {
            "id": "es-PR-VictorNeural",
            "name": "Víctor",
            "gender": "Masculino",
            "accent": "Puerto Rico",
            "category": "Centroamérica y Caribe",
            "recommended": False,
            "description": "Locución dinámica y articulada.",
            "engine": "edge-tts"
        },
        {
            "id": "es-PR-KarinaNeural",
            "name": "Karina",
            "gender": "Femenino",
            "accent": "Puerto Rico",
            "category": "Centroamérica y Caribe",
            "recommended": False,
            "description": "Voz alegre, profesional y expresiva.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-AlonsoNeural",
            "name": "Alonso",
            "gender": "Masculino",
            "accent": "Latino Neutro (EE.UU.)",
            "category": "Latino Neutro (EE.UU.)",
            "recommended": False,
            "description": "Locución dinámica y articulada para presentaciones corporativas.",
            "engine": "edge-tts"
        },
        {
            "id": "es-US-PalomaNeural",
            "name": "Paloma",
            "gender": "Femenino",
            "accent": "Latino Neutro (EE.UU.)",
            "category": "Latino Neutro (EE.UU.)",
            "recommended": False,
            "description": "Tono joven, fresco y claro.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-AlvaroNeural",
            "name": "Álvaro",
            "gender": "Masculino",
            "accent": "España",
            "category": "Castellano (España)",
            "recommended": False,
            "description": "Acento castellano formal y bien articulado.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-ElviraNeural",
            "name": "Elvira",
            "gender": "Femenino",
            "accent": "España",
            "category": "Castellano (España)",
            "recommended": False,
            "description": "Acento castellano clásico y sereno.",
            "engine": "edge-tts"
        },
        {
            "id": "es-ES-XimenaNeural",
            "name": "Ximena",
            "gender": "Femenino",
            "accent": "España",
            "category": "Castellano (España)",
            "recommended": False,
            "description": "Voz castellana juvenil y expresiva.",
            "engine": "edge-tts"
        },
    ],
    "en": [
        # --- XIAOMI MIMO V2.5 (DIRECTOR MODE + EMOTIONS) ---
        {
            "id": "mimo-Chloe",
            "name": "Chloe (Xiaomi MiMo)",
            "gender": "Femenino",
            "accent": "American",
            "category": "⭐ Xiaomi MiMo (Director Mode + Emotions)",
            "recommended": True,
            "description": "Ultra-expressive AI voice with natural language Director Mode control and inline audio tags like [laughter] or [sigh].",
            "engine": "mimo"
        },
        {
            "id": "mimo-Mia",
            "name": "Mia (Xiaomi MiMo)",
            "gender": "Femenino",
            "accent": "American",
            "category": "⭐ Xiaomi MiMo (Director Mode + Emotions)",
            "recommended": False,
            "description": "Warm, engaging female voice for storytelling, podcasts, and conversational lessons.",
            "engine": "mimo"
        },
        {
            "id": "mimo-Milo",
            "name": "Milo (Xiaomi MiMo)",
            "gender": "Masculino",
            "accent": "American",
            "category": "⭐ Xiaomi MiMo (Director Mode + Emotions)",
            "recommended": False,
            "description": "Bright, energetic, and youthful male voice.",
            "engine": "mimo"
        },
        {
            "id": "mimo-Dean",
            "name": "Dean (Xiaomi MiMo)",
            "gender": "Masculino",
            "accent": "American",
            "category": "⭐ Xiaomi MiMo (Director Mode + Emotions)",
            "recommended": False,
            "description": "Authoritative, resonant, and documentary-style male voice.",
            "engine": "mimo"
        },
        # --- MEZCLAS EDUCATIVAS (VOICE BLENDING) ---
        {
            "id": "af_bella,af_sarah",
            "name": "Bella & Sarah (Mezcla Educativa)",
            "gender": "Femenino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": True,
            "description": "Mezcla estelar recomendada para e-learning: combina la claridad nítida de Bella con el ritmo cálido y pausado de Sarah.",
            "engine": "kokoro"
        },
        {
            "id": "af_heart,af_nicole",
            "name": "Heart & Nicole (Mezcla Didáctica)",
            "gender": "Femenino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": False,
            "description": "Fusión de calidez empática y articulación metódica para tutoriales paso a paso.",
            "engine": "kokoro"
        },
        {
            "id": "am_adam,am_michael",
            "name": "Adam & Michael (Mezcla Académica)",
            "gender": "Masculino",
            "accent": "American Blend",
            "category": "⭐ Mezclas Educativas (Blends)",
            "recommended": False,
            "description": "Tono documental formal y robusto para conferencias o lecciones científicas.",
            "engine": "kokoro"
        },
        # --- AMERICAN FEMALE (11 VOCES) ---
        {
            "id": "af_heart",
            "name": "Heart (Insignia Kokoro)",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": True,
            "description": "Voz insignia de Kokoro. Calidez humana insuperable y máxima naturalidad para e-learning.",
            "engine": "kokoro"
        },
        {
            "id": "af_bella",
            "name": "Bella",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Articulada, expresiva y didáctica.",
            "engine": "kokoro"
        },
        {
            "id": "af_sarah",
            "name": "Sarah",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Voz juvenil, amigable y entusiasta con ritmo cadencioso.",
            "engine": "kokoro"
        },
        {
            "id": "af_nicole",
            "name": "Nicole",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono paciente y profesional, perfecto para guías instructivas.",
            "engine": "kokoro"
        },
        {
            "id": "af_alloy",
            "name": "Alloy",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono versátil y directo, similar a asistentes modernos.",
            "engine": "kokoro"
        },
        {
            "id": "af_aoede",
            "name": "Aoede",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono suave, fluido y envolvente.",
            "engine": "kokoro"
        },
        {
            "id": "af_jessica",
            "name": "Jessica",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Locución clara y formal para presentaciones de negocios.",
            "engine": "kokoro"
        },
        {
            "id": "af_kore",
            "name": "Kore",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono calmo y seguro para lecturas reflexivas.",
            "engine": "kokoro"
        },
        {
            "id": "af_nova",
            "name": "Nova",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Energética, dinámica y motivacional.",
            "engine": "kokoro"
        },
        {
            "id": "af_river",
            "name": "River",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Tono moderno con textura acústica natural.",
            "engine": "kokoro"
        },
        {
            "id": "af_sky",
            "name": "Sky",
            "gender": "Femenino",
            "accent": "American",
            "category": "American Female (US)",
            "recommended": False,
            "description": "Voz luminosa y positiva para módulos de bienvenida o síntesis.",
            "engine": "kokoro"
        },
        # --- AMERICAN MALE (9 VOCES) ---
        {
            "id": "am_adam",
            "name": "Adam (Recomendado)",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": True,
            "description": "Narrador clásico estilo documental y conferencias académicas.",
            "engine": "kokoro"
        },
        {
            "id": "am_michael",
            "name": "Michael",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz madura y técnica para temas científicos.",
            "engine": "kokoro"
        },
        {
            "id": "am_echo",
            "name": "Echo",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono pausado, ideal para meditaciones o lecturas reflexivas.",
            "engine": "kokoro"
        },
        {
            "id": "am_eric",
            "name": "Eric",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Locución amena y conversacional para talleres prácticos.",
            "engine": "kokoro"
        },
        {
            "id": "am_fenrir",
            "name": "Fenrir",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz profunda y resonante para narraciones dramáticas.",
            "engine": "kokoro"
        },
        {
            "id": "am_liam",
            "name": "Liam",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono joven y dinámico para audiencias jóvenes o universitarias.",
            "engine": "kokoro"
        },
        {
            "id": "am_onyx",
            "name": "Onyx",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz grave y autorizada para síntesis conceptuales.",
            "engine": "kokoro"
        },
        {
            "id": "am_puck",
            "name": "Puck",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Voz ágil y espontánea.",
            "engine": "kokoro"
        },
        {
            "id": "am_santa",
            "name": "Santa",
            "gender": "Masculino",
            "accent": "American",
            "category": "American Male (US)",
            "recommended": False,
            "description": "Tono cálido, festivo y característico.",
            "engine": "kokoro"
        },
        # --- BRITISH FEMALE (4 VOCES) ---
        {
            "id": "bf_emma",
            "name": "Emma (Académica UK)",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Acento británico elegante y pedagógico.",
            "engine": "kokoro"
        },
        {
            "id": "bf_alice",
            "name": "Alice",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Voz británica articulada y refinada.",
            "engine": "kokoro"
        },
        {
            "id": "bf_isabella",
            "name": "Isabella",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Voz británica formal y suave.",
            "engine": "kokoro"
        },
        {
            "id": "bf_lily",
            "name": "Lily",
            "gender": "Femenino",
            "accent": "British",
            "category": "British Female (UK)",
            "recommended": False,
            "description": "Tono joven británico, claro y melodioso.",
            "engine": "kokoro"
        },
        # --- BRITISH MALE (4 VOCES) ---
        {
            "id": "bm_george",
            "name": "George (Académico UK)",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Narrador clásico británico con presencia autorizada.",
            "engine": "kokoro"
        },
        {
            "id": "bm_daniel",
            "name": "Daniel",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Voz británica sobria y catedrática.",
            "engine": "kokoro"
        },
        {
            "id": "bm_fable",
            "name": "Fable",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Estilo cuenta-cuentos o narrador literario británico.",
            "engine": "kokoro"
        },
        {
            "id": "bm_lewis",
            "name": "Lewis",
            "gender": "Masculino",
            "accent": "British",
            "category": "British Male (UK)",
            "recommended": False,
            "description": "Voz británica precisa y clara.",
            "engine": "kokoro"
        },
    ]
}

# Kokoro voice IDs quick lookup set
KOKORO_VOICES = {v["id"] for v_list in VOICES_CATALOG.values() for v in v_list if v.get("engine") == "kokoro"}

# MiMo voice IDs quick lookup set
MIMO_VOICES = {v["id"] for v_list in VOICES_CATALOG.values() for v in v_list if v.get("engine") == "mimo"}
