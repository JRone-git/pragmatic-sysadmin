/* ========== BUDDY i18n — Translations ==========
 * 6 languages: English, Spanish, French, German, Portuguese (BR), Chinese (Simplified)
 * To add a new language: copy 'en', change the codes, translate values.
 * To use: include this file before app.js.
 */

const TRANSLATIONS = {

  /* ====================== ENGLISH ====================== */
  en: {
    meta: {
      name: "English",
      nativeName: "English",
      code: "en",
      flag: "🇺🇸",
      dateLocale: "en-US",
      emergencyNumber: "911"
    },
    app: {
      brandLine: "Your Everyday Helper",
      greeting: "Hi, I'm {name}",
      madeWith: "Made with care by"
    },
    time: {
      morning: "Good morning ☀️",
      afternoon: "Good afternoon 🌤️",
      evening: "Good evening 🌙"
    },
    tiles: {
      people: { label: "My People", sub: "Family & friends" },
      meds:  { label: "Medicines", sub: "Reminders & check-off" },
      notes: { label: "My Notes", sub: "Reminders & notes" },
      safety:{ label: "Stay Safe", sub: "Scam check, trusted calls" },
      help:  { label: "How-To", sub: "Step-by-step guides" }
    },
    emergency: "Emergency — Tap to Call {number}",
    upgrade: {
      title: "Buddy Plus",
      text: "— unlimited contacts, scam check, family dashboard",
      button: "$7/month",
      comingSoon: "Buddy Plus is coming soon",
      modalBody: "Leave your email and we'll let you know when it launches. We'll also send you a free guide: \"5 Conversations to Have with Your Aging Parent About Online Safety.\"",
      emailLabel: "Email",
      notNow: "Not now",
      notify: "Notify Me",
      badEmail: "Please enter a valid email.",
      saved: "✓ You're on the list!"
    },
    checkin: {
      title: "Today's Check-in",
      empty: "Add your medicines to track them.",
      pending: "{n} medicine{s} to take today",
      partial: "{taken} of {total} taken today",
      done: "All {total} done — great job! 🎉"
    },
    nav: {
      backHome: "← Back to Home",
      backHelp: "← Back to How-To",
      backToHelp: "← Back to How-To",
      language: "Language"
    },
    people: {
      title: "My People",
      hint: "Tap **Call** to ring someone right away.",
      empty: "No people added yet. Tap \"+ Add a Person\" below.",
      add: "+ Add a Person",
      addTitle: "Add a Person",
      delete: "×",
      removeConfirm: "Remove {name}?"
    },
    meds: {
      title: "My Medicines",
      hint: "Tap the green circle when you take a medicine. It resets every day.",
      empty: "No medicines added yet. Tap \"+ Add a Medicine\" below.",
      add: "+ Add a Medicine",
      addTitle: "Add a Medicine",
      taken: "✓ Taken!",
      removeConfirm: "Remove {name}?",
      alarm: "Alarm",
      alarmNotify: "⏰ Time to take {name} ({time})"
    },
    notes: {
      title: "My Notes",
      hint: "Write down anything you want to remember. Notes with a bell will send you a reminder.",
      empty: "No notes yet. Tap \"+ Add a Note\" below.",
      add: "+ Add a Note",
      addTitle: "Add a Note",
      noteText: "What do you want to remember?",
      placeholderNote: "e.g. Call the bank on Friday, pick up groceries…",
      alarmTime: "Reminder time (optional)",
      alarmHint: "Buddy will send you a notification at this time. Leave empty for no reminder.",
      noAlarm: "No reminder",
      alarmNotify: "⏰ Reminder: {text}… ({time})",
      delete: "Delete note",
      removeConfirm: "Delete this note?"
    },
    onboarding: {
      welcomeTitle: "Welcome to Buddy!",
      welcomeText: "Buddy is your simple everyday helper. Let me show you around — it only takes a moment.",
      peopleTitle: "My People",
      peopleText: "Add your family and friends here. Then you can call them with just one tap — no need to search your contacts.",
      medsTitle: "Medicine Reminders",
      medsText: "Add your medicines and tap the green circle when you take them. You can also turn on alarms — Buddy will notify you when it's time.",
      safetyTitle: "You're All Set!",
      safetyText: "If you ever get a suspicious message, use the Stay Safe checker. And the red emergency button is always there if you need it. Tap Done to start!",
      skip: "Skip",
      next: "Next",
      done: "Done ✓"
    },
    safety: {
      title: "Stay Safe",
      checkTitle: "Is this message a scam?",
      checkHint: "Got a weird text, email, or voicemail? Paste it here and Buddy will look for the warning signs.",
      checkButton: "Check This Message",
      placeholder: "Paste the message here…",
      tooShort: "⚠️ Please paste the full message — I need at least a sentence or two to check it.",
      clean: "✅ I don't see the usual warning signs. That doesn't mean it's 100% safe — when in doubt, call the person or company directly using a phone number you look up yourself (not one from the message).",
      risky: "🚨 This looks risky. I spotted {n} warning sign{s}: {hits}. Don't click any links. Don't send money or share codes. Call someone you trust before doing anything.",
      trustedTitle: "Trusted Numbers",
      trustedHint: "These are the people you trust. If they ask for money or info, double-check by calling them back on a number you know is theirs.",
      emptyTrusted: "Add people you trust from \"My People\" on the home screen.",
      call911: "🚨 Call {number}"
    },
    help: {
      title: "How Can I Help?",
      hint: "Step-by-step guides for common phone tasks."
    },
    form: {
      name: "Name",
      phone: "Phone number",
      relation: "How are they related? (optional)",
      medTime: "When to take it",
      notes: "Notes (optional)",
      email: "Email",
      placeholderPersonName: "e.g. Sarah (daughter)",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "e.g. Family, Doctor, Neighbor",
      placeholderMedName: "e.g. Blood pressure pill",
      placeholderMedTime: "e.g. Morning, Noon, Evening, Bedtime",
      placeholderNotes: "e.g. Take with food",
      placeholderEmail: "you@example.com",
      cancel: "Cancel",
      save: "Save",
      needName: "Please enter a name.",
      needPhone: "Please enter a phone number so the Call button works."
    },
    scamPatterns: {
      urgency: "Urgency pressure",
      payment: "Unusual payment request",
      authority: "Authority impersonation",
      verify: "Account verification ask",
      link: "Pushes you to click a link",
      prize: "Prize/lottery language",
      sensitive: "Asks for sensitive info",
      familyEmergency: "Family emergency scam",
      threat: "Fear-based threats",
      fakeCompany: "Fake company notice"
    },
    topics: {
      screenshotIphone: {
        title: "How to take a screenshot (iPhone)",
        steps: [
          "Look at the screen you want to capture.",
          "Press the Side button (right edge) and the Volume Up button (left edge) at the SAME time.",
          "Let go quickly. The screen will flash white.",
          "The picture is saved in your Photos app. Open Photos to find it."
        ]
      },
      screenshotAndroid: {
        title: "How to take a screenshot (Android)",
        steps: [
          "Look at the screen you want to capture.",
          "Press the Power button (right edge) and the Volume Down button at the SAME time.",
          "Let go quickly. You'll hear a click or see a flash.",
          "The picture is saved in your Photos or Gallery app."
        ]
      },
      facetime: {
        title: "How to video call your family (iPhone)",
        steps: [
          "Open the FaceTime app. It's a green icon with a white video camera.",
          "Tap the person you want to call from your contacts.",
          "Tap the round video camera button (not the phone one).",
          "Wait for them to answer. Wave hi!",
          "Tap the red phone button when you're done to hang up."
        ]
      },
      duo: {
        title: "How to video call your family (Android)",
        steps: [
          "Open the Google Meet or Duo app.",
          "Tap Search contacts at the top.",
          "Pick the person you want to call.",
          "Tap the video camera button.",
          "Wait for them to answer. Tap the red button to hang up."
        ]
      },
      sendphoto: {
        title: "How to send a photo by text",
        steps: [
          "Open the Messages app. It's a green icon with a white speech bubble.",
          "Tap on the conversation with the person you want to send to.",
          "Tap the camera icon (📷) next to the typing area.",
          "Pick the photo you want from your camera roll.",
          "Tap the blue arrow to send it."
        ]
      },
      wifi: {
        title: "How to connect to Wi-Fi",
        steps: [
          "Open Settings. Look for a gray gear icon ⚙️ on your home screen.",
          "Tap Wi-Fi.",
          "You'll see a list of network names. Tap your home network.",
          "Type the password. It's usually on a sticker on your Wi-Fi router.",
          "Tap Join or Connect. You're online when you see a blue check mark."
        ]
      },
      update: {
        title: "How to update your phone",
        steps: [
          "Plug your phone into a charger. Updates need power.",
          "Make sure you're connected to Wi-Fi.",
          "Open Settings ⚙️.",
          "Tap General (iPhone) or System (Android).",
          "Tap Software Update.",
          "Tap Download and Install. Wait — don't unplug! It can take 15-30 minutes."
        ]
      },
      password: {
        title: "I forgot my password",
        steps: [
          "On the screen where it asks for your password, look for \"Forgot password?\"",
          "Tap it.",
          "Enter your email or phone number when asked.",
          "Check your email or text messages for a code.",
          "Type in the code.",
          "Make a new password you'll remember. Write it down on paper and keep it safe!"
        ]
      },
      textsize: {
        title: "How to make text bigger",
        steps: [
          "Open Settings ⚙️.",
          "Tap Display & Brightness (iPhone) or Display (Android).",
          "Tap Text Size.",
          "Drag the slider to the right to make text bigger.",
          "You can also turn on \"Bold Text\" for easier reading."
        ]
      },
      ringtone: {
        title: "How to make my phone ring louder",
        steps: [
          "Look on the left side of your phone. You'll see two buttons.",
          "The top button makes it louder. The bottom one makes it quieter.",
          "Press the TOP button many times until you see the volume all the way up.",
          "If it's still quiet, open Settings ⚙️, then Sounds, and turn off \"Silent Mode\"."
        ]
      }
    },
    toast: {
      added: "Added",
      removed: "Removed"
    },
    feedback: {
      prompt: "How is Buddy working for you?",
      easy: "Easy 👍",
      hard: "Hard 👎",
      thanks: "Thanks for the feedback!",
      easyThanks: "Glad to hear it!",
      hardSorry: "Sorry about that. What was hard?",
      placeholder: "What was confusing? (optional)",
      send: "Send",
      skip: "Skip",
      sent: "✓ Thanks!",
      shareTitle: "Know someone who'd like Buddy?",
      shareBody: "I'm using Buddy — a simple app for older family members. One-tap calls to family, medicine reminders, scam checker. Free, no signup.",
      shareButton: "Share Buddy"
    }
  },

  /* ====================== SPANISH ====================== */
  es: {
    meta: {
      name: "Spanish",
      nativeName: "Español",
      code: "es",
      flag: "🇪🇸",
      dateLocale: "es-ES",
      emergencyNumber: "911"
    },
    app: {
      brandLine: "Tu ayudante cotidiano",
      greeting: "Hola, soy {name}",
      madeWith: "Hecho con cariño por"
    },
    time: {
      morning: "Buenos días ☀️",
      afternoon: "Buenas tardes 🌤️",
      evening: "Buenas noches 🌙"
    },
    tiles: {
      people: { label: "Mis Personas", sub: "Familia y amigos" },
      meds:  { label: "Medicinas", sub: "Recordatorios y checks" },
      notes: { label: "Mis Notas", sub: "Recordatorios y notas" },
      safety:{ label: "Seguridad", sub: "Detector de estafas" },
      help:  { label: "Cómo Hacer", sub: "Guías paso a paso" }
    },
    emergency: "Emergencia — Toca para Llamar al {number}",
    upgrade: {
      title: "Buddy Plus",
      text: "— contactos ilimitados, detector de estafas, panel familiar",
      button: "$7/mes",
      comingSoon: "Buddy Plus viene pronto",
      modalBody: "Deja tu correo y te avisaremos cuando se lance. También te enviaremos una guía gratis: \"5 Conversaciones Para Tener Con Tu Padre Sobre Seguridad En Línea.\"",
      emailLabel: "Correo electrónico",
      notNow: "Ahora no",
      notify: "Avísame",
      badEmail: "Por favor, ingresa un correo válido.",
      saved: "✓ ¡Estás en la lista!"
    },
    checkin: {
      title: "Chequeo de Hoy",
      empty: "Agrega tus medicinas para rastrearlas.",
      pending: "{n} medicina{s} para tomar hoy",
      partial: "{taken} de {total} tomada{s} hoy",
      done: "¡Las {total} listas — bien hecho! 🎉"
    },
    nav: {
      backHome: "← Volver al Inicio",
      backHelp: "← Volver a Cómo Hacer",
      backToHelp: "← Volver a Cómo Hacer",
      language: "Idioma"
    },
    people: {
      title: "Mis Personas",
      hint: "Toca **Llamar** para llamar a alguien ahora mismo.",
      empty: "Aún no has agregado personas. Toca \"+ Agregar Persona\" abajo.",
      add: "+ Agregar Persona",
      addTitle: "Agregar Persona",
      delete: "×",
      removeConfirm: "¿Eliminar a {name}?"
    },
    meds: {
      title: "Mis Medicinas",
      hint: "Toca el círculo verde cuando tomes una medicina. Se reinicia cada día.",
      empty: "Aún no has agregado medicinas. Toca \"+ Agregar Medicina\" abajo.",
      add: "+ Agregar Medicina",
      addTitle: "Agregar Medicina",
      taken: "✓ ¡Tomada!",
      removeConfirm: "¿Eliminar {name}?",
      alarm: "Alarma",
      alarmNotify: "⏰ Hora de tomar {name} ({time})"
    },
    notes: {
      title: "Mis Notas",
      hint: "Escribe lo que quieras recordar. Las notas con campana te enviarán un recordatorio.",
      empty: "Sin notas todavía. Toca \"+ Añadir nota\" abajo.",
      add: "+ Añadir nota",
      addTitle: "Añadir nota",
      noteText: "¿Qué quieres recordar?",
      placeholderNote: "ej. Llamar al banco el viernes, comprar comida…",
      alarmTime: "Hora del recordatorio (opcional)",
      alarmHint: "Buddy te enviará una notificación a esta hora. Déjalo vacío si no quieres recordatorio.",
      noAlarm: "Sin recordatorio",
      alarmNotify: "⏰ Recordatorio: {text}… ({time})",
      delete: "Borrar nota",
      removeConfirm: "¿Borrar esta nota?"
    },
    onboarding: {
      welcomeTitle: "¡Bienvenido a Buddy!",
      welcomeText: "Buddy es tu ayudante diario. Te lo muestro en un momento.",
      peopleTitle: "Mi Gente",
      peopleText: "Añade a tu familia y amigos aquí. Podrás llamarles con un solo toque.",
      medsTitle: "Recordatorios de medicinas",
      medsText: "Añade tus medicinas y toca el círculo verde al tomarlas. También puedes activar alarmas.",
      safetyTitle: "¡Todo listo!",
      safetyText: "Si recibes un mensaje sospechoso, usa el comprobador de seguridad. Y el botón rojo de emergencia siempre está ahí.",
      skip: "Omitir",
      next: "Siguiente",
      done: "Listo ✓"
    },
    safety: {
      title: "Seguridad",
      checkTitle: "¿Es este mensaje una estafa?",
      checkHint: "¿Recibiste un mensaje raro? Pégalo aquí y Buddy buscará señales de alerta.",
      checkButton: "Revisar Este Mensaje",
      placeholder: "Pega el mensaje aquí…",
      tooShort: "⚠️ Pega el mensaje completo — necesito al menos una o dos frases para revisarlo.",
      clean: "✅ No veo las señales de alerta usuales. Eso no significa que sea 100% seguro — si tienes dudas, llama directamente usando un número que tú mismo busques.",
      risky: "🚨 Esto parece riesgoso. Detecté {n} señal{s} de alerta: {hits}. No hagas clic en enlaces. No envíes dinero ni códigos. Llama a alguien de confianza antes de actuar.",
      trustedTitle: "Números de Confianza",
      trustedHint: "Estas son las personas en las que confías. Si piden dinero, verifica llamándolas a un número que ya conoces.",
      emptyTrusted: "Agrega personas de confianza desde \"Mis Personas\" en el inicio.",
      call911: "🚨 Llamar al {number}"
    },
    help: {
      title: "¿Cómo Puedo Ayudar?",
      hint: "Guías paso a paso para tareas comunes del teléfono."
    },
    form: {
      name: "Nombre",
      phone: "Número de teléfono",
      relation: "¿Cómo se relaciona? (opcional)",
      medTime: "Cuándo tomarla",
      notes: "Notas (opcional)",
      email: "Correo electrónico",
      placeholderPersonName: "ej. Sara (hija)",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "ej. Familia, Doctor, Vecino",
      placeholderMedName: "ej. Pastilla para la presión",
      placeholderMedTime: "ej. Mañana, Mediodía, Noche",
      placeholderNotes: "ej. Con comida",
      placeholderEmail: "tu@correo.com",
      cancel: "Cancelar",
      save: "Guardar",
      needName: "Por favor, ingresa un nombre.",
      needPhone: "Por favor, ingresa un número de teléfono para que Llamar funcione."
    },
    scamPatterns: {
      urgency: "Presión de urgencia",
      payment: "Pago inusual",
      authority: "Suplantación de autoridad",
      verify: "Pide verificar cuenta",
      link: "Empuja a hacer clic",
      prize: "Lenguaje de premio",
      sensitive: "Pide información sensible",
      familyEmergency: "Estafa familiar de emergencia",
      threat: "Amenazas de miedo",
      fakeCompany: "Aviso falso de empresa"
    },
    topics: {
      screenshotIphone: {
        title: "Cómo tomar una captura de pantalla (iPhone)",
        steps: [
          "Mira la pantalla que quieres capturar.",
          "Presiona el botón lateral (borde derecho) y el botón de Subir Volumen (borde izquierdo) AL MISMO TIEMPO.",
          "Suéltalos rápido. La pantalla parpadeará en blanco.",
          "La imagen se guarda en tu app de Fotos. Abre Fotos para encontrarla."
        ]
      },
      screenshotAndroid: {
        title: "Cómo tomar una captura de pantalla (Android)",
        steps: [
          "Mira la pantalla que quieres capturar.",
          "Presiona el botón de Encendido (borde derecho) y el botón de Bajar Volumen AL MISMO TIEMPO.",
          "Suéltalos rápido. Escucharás un clic o verás un flash.",
          "La imagen se guarda en tu app de Fotos o Galería."
        ]
      },
      facetime: {
        title: "Cómo hacer videollamada a tu familia (iPhone)",
        steps: [
          "Abre la app FaceTime. Es un ícono verde con una cámara de video blanca.",
          "Toca a la persona que quieres llamar de tus contactos.",
          "Toca el botón redondo de la cámara de video (no el del teléfono).",
          "Espera a que contesten. ¡Saluda!",
          "Toca el botón rojo del teléfono cuando termines para colgar."
        ]
      },
      duo: {
        title: "Cómo hacer videollamada a tu familia (Android)",
        steps: [
          "Abre la app Google Meet o Duo.",
          "Toca Buscar contactos arriba.",
          "Elige a la persona que quieres llamar.",
          "Toca el botón de la cámara de video.",
          "Espera a que contesten. Toca el botón rojo para colgar."
        ]
      },
      sendphoto: {
        title: "Cómo enviar una foto por mensaje",
        steps: [
          "Abre la app de Mensajes. Es un ícono verde con un globo blanco.",
          "Toca la conversación con la persona a la que quieres enviar.",
          "Toca el ícono de cámara (📷) junto al área de escritura.",
          "Elige la foto que quieres de tu carrete.",
          "Toca la flecha azul para enviarla."
        ]
      },
      wifi: {
        title: "Cómo conectarse a Wi-Fi",
        steps: [
          "Abre Ajustes. Busca un ícono gris de engranaje ⚙️ en tu pantalla de inicio.",
          "Toca Wi-Fi.",
          "Verás una lista de redes. Toca tu red de casa.",
          "Escribe la contraseña. Usually está en una etiqueta en tu router.",
          "Toca Unirse o Conectar. Estás conectado cuando veas una palomita azul."
        ]
      },
      update: {
        title: "Cómo actualizar tu teléfono",
        steps: [
          "Conecta tu teléfono a un cargador. Las actualizaciones necesitan energía.",
          "Asegúrate de estar conectado a Wi-Fi.",
          "Abre Ajustes ⚙️.",
          "Toca General (iPhone) o Sistema (Android).",
          "Toca Actualización de Software.",
          "Toca Descargar e Instalar. ¡Espera — no desconectes! Tarda 15-30 minutos."
        ]
      },
      password: {
        title: "Olvidé mi contraseña",
        steps: [
          "Donde pide tu contraseña, busca \"¿Olvidaste tu contraseña?\"",
          "Tócala.",
          "Ingresa tu correo o número de teléfono.",
          "Revisa tu correo o mensajes para un código.",
          "Escribe el código.",
          "Crea una nueva contraseña que recuerdes. ¡Anótala en papel y guárdala!"
        ]
      },
      textsize: {
        title: "Cómo agrandar el texto",
        steps: [
          "Abre Ajustes ⚙️.",
          "Toca Pantalla y Brillo (iPhone) o Pantalla (Android).",
          "Toca Tamaño del Texto.",
          "Arrastra el control a la derecha para hacer el texto más grande.",
          "También puedes activar \"Texto en Negrita\" para leer mejor."
        ]
      },
      ringtone: {
        title: "Cómo hacer que suene más fuerte mi teléfono",
        steps: [
          "Mira el lado izquierdo de tu teléfono. Verás dos botones.",
          "El botón superior sube el volumen. El inferior lo baja.",
          "Presiona el botón SUPERIOR muchas veces hasta que esté al máximo.",
          "Si sigue bajo, abre Ajustes ⚙️, luego Sonidos, y desactiva \"Modo Silencio\"."
        ]
      }
    },
    toast: {
      added: "Agregado",
      removed: "Eliminado"
    },
    feedback: {
      prompt: "¿Qué tal te va con Buddy?",
      easy: "Fácil 👍",
      hard: "Difícil 👎",
      thanks: "¡Gracias por tu opinión!",
      easyThanks: "¡Me alegra!",
      hardSorry: "Lo siento. ¿Qué fue difícil?",
      placeholder: "¿Qué fue confuso? (opcional)",
      send: "Enviar",
      skip: "Omitir",
      sent: "✓ ¡Gracias!",
      shareTitle: "¿Conoces a alguien a quien le gustaría Buddy?",
      shareBody: "Estoy usando Buddy — una app sencilla para familiares mayores. Llamadas con un toque, recordatorios de medicinas, detector de estafas. Gratis, sin registro.",
      shareButton: "Compartir Buddy"
    }
  },

  /* ====================== FRENCH ====================== */
  fr: {
    meta: {
      name: "French",
      nativeName: "Français",
      code: "fr",
      flag: "🇫🇷",
      dateLocale: "fr-FR",
      emergencyNumber: "112"
    },
    app: {
      brandLine: "Votre assistant au quotidien",
      greeting: "Bonjour, je suis {name}",
      madeWith: "Fait avec soin par"
    },
    time: {
      morning: "Bonjour ☀️",
      afternoon: "Bon après-midi 🌤️",
      evening: "Bonsoir 🌙"
    },
    tiles: {
      people: { label: "Mes Proches", sub: "Famille et amis" },
      meds:  { label: "Médicaments", sub: "Rappels et suivi" },
      notes: { label: "Mes Notes", sub: "Rappels et notes" },
      safety:{ label: "En Sécurité", sub: "Vérifier les arnaques" },
      help:  { label: "Comment Faire", sub: "Guides étape par étape" }
    },
    emergency: "Urgence — Appuyez pour appeler le {number}",
    upgrade: {
      title: "Buddy Plus",
      text: "— contacts illimités, détecteur d'arnaques, tableau familial",
      button: "7 $/mois",
      comingSoon: "Buddy Plus arrive bientôt",
      modalBody: "Laissez votre email et nous vous préviendrons au lancement. Nous vous enverrons aussi un guide gratuit : \"5 conversations à avoir avec votre parent âgé sur la sécurité en ligne.\"",
      emailLabel: "Email",
      notNow: "Pas maintenant",
      notify: "Me prévenir",
      badEmail: "Veuillez entrer un email valide.",
      saved: "✓ Vous êtes inscrit !"
    },
    checkin: {
      title: "Bilan du Jour",
      empty: "Ajoutez vos médicaments pour les suivre.",
      pending: "{n} médicament{s} à prendre aujourd'hui",
      partial: "{taken} sur {total} pris aujourd'hui",
      done: "Les {total} pris — bravo ! 🎉"
    },
    nav: {
      backHome: "← Retour à l'accueil",
      backHelp: "← Retour à Comment Faire",
      backToHelp: "← Retour à Comment Faire",
      language: "Langue"
    },
    people: {
      title: "Mes Proches",
      hint: "Appuyez sur **Appeler** pour joindre quelqu'un tout de suite.",
      empty: "Aucun proche ajouté. Appuyez sur \"+ Ajouter une personne\" ci-dessous.",
      add: "+ Ajouter une personne",
      addTitle: "Ajouter une personne",
      delete: "×",
      removeConfirm: "Supprimer {name} ?"
    },
    meds: {
      title: "Mes Médicaments",
      hint: "Appuyez sur le cercle vert quand vous prenez un médicament. Réinitialisé chaque jour.",
      empty: "Aucun médicament ajouté. Appuyez sur \"+ Ajouter un médicament\" ci-dessous.",
      add: "+ Ajouter un médicament",
      addTitle: "Ajouter un médicament",
      taken: "✓ Pris !",
      removeConfirm: "Supprimer {name} ?",
      alarm: "Alarme",
      alarmNotify: "⏰ Il est temps de prendre {name} ({time})"
    },
    notes: {
      title: "Mes Notes",
      hint: "Écrivez ce que vous voulez retenir. Les notes avec une cloche enverront un rappel.",
      empty: "Pas encore de notes. Appuyez sur \"+ Ajouter une note\" ci-dessous.",
      add: "+ Ajouter une note",
      addTitle: "Ajouter une note",
      noteText: "Que voulez-vous retenir ?",
      placeholderNote: "ex. Appeler la banque vendredi, faire les courses…",
      alarmTime: "Heure du rappel (facultatif)",
      alarmHint: "Buddy enverra une notification à cette heure. Laissez vide pour aucun rappel.",
      noAlarm: "Pas de rappel",
      alarmNotify: "⏰ Rappel : {text}… ({time})",
      delete: "Supprimer la note",
      removeConfirm: "Supprimer cette note ?"
    },
    onboarding: {
      welcomeTitle: "Bienvenue sur Buddy !",
      welcomeText: "Buddy est votre assistant quotidien simple. Laissez-moi vous montrer — ça ne prend qu'un moment.",
      peopleTitle: "Mes Proches",
      peopleText: "Ajoutez votre famille et vos amis ici. Vous pourrez les appeler en un seul tap.",
      medsTitle: "Rappels de médicaments",
      medsText: "Ajoutez vos médicaments et appuyez sur le cercle vert quand vous les prenez. Vous pouvez aussi activer les alarmes.",
      safetyTitle: "Tout est prêt !",
      safetyText: "Si vous recevez un message suspect, utilisez le vérificateur de sécurité. Et le bouton d'urgence rouge est toujours là.",
      skip: "Passer",
      next: "Suivant",
      done: "C'est fait ✓"
    },
    safety: {
      title: "En Sécurité",
      checkTitle: "Ce message est-il une arnaque ?",
      checkHint: "Vous avez reçu un message bizarre ? Collez-le ici et Buddy cherchera les signes d'alerte.",
      checkButton: "Vérifier ce message",
      placeholder: "Collez le message ici…",
      tooShort: "⚠️ Collez le message complet — j'ai besoin d'au moins une ou deux phrases.",
      clean: "✅ Je ne vois pas les signes d'alerte habituels. Cela ne signifie pas que c'est sûr à 100 % — en cas de doute, appelez directement en utilisant un numéro que vous avez trouvé vous-même.",
      risky: "🚨 Cela semble risqué. J'ai repéré {n} signe{s} d'alerte : {hits}. Ne cliquez pas sur les liens. N'envoyez pas d'argent ni de codes. Appelez quelqu'un de confiance avant d'agir.",
      trustedTitle: "Numéros de confiance",
      trustedHint: "Voici les personnes en qui vous avez confiance. Si elles demandent de l'argent, vérifiez en les rappelant à un numéro que vous connaissez.",
      emptyTrusted: "Ajoutez des proches de confiance depuis \"Mes Proches\" sur l'accueil.",
      call911: "🚨 Appeler le {number}"
    },
    help: {
      title: "Comment Puis-je Aider ?",
      hint: "Guides étape par étape pour les tâches courantes sur téléphone."
    },
    form: {
      name: "Nom",
      phone: "Numéro de téléphone",
      relation: "Quel est le lien ? (optionnel)",
      medTime: "Quand le prendre",
      notes: "Notes (optionnel)",
      email: "Email",
      placeholderPersonName: "ex. Sarah (fille)",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "ex. Famille, Médecin, Voisin",
      placeholderMedName: "ex. Pilule pour la tension",
      placeholderMedTime: "ex. Matin, Midi, Soir, Coucher",
      placeholderNotes: "ex. Avec de la nourriture",
      placeholderEmail: "vous@exemple.com",
      cancel: "Annuler",
      save: "Enregistrer",
      needName: "Veuillez entrer un nom.",
      needPhone: "Veuillez entrer un numéro pour que le bouton Appeler fonctionne."
    },
    scamPatterns: {
      urgency: "Pression d'urgence",
      payment: "Paiement inhabituel",
      authority: "Usurpation d'autorité",
      verify: "Demande de vérification de compte",
      link: "Pousse à cliquer un lien",
      prize: "Langage de loterie",
      sensitive: "Demande d'infos sensibles",
      familyEmergency: "Arnaque urgence familiale",
      threat: "Menaces effrayantes",
      fakeCompany: "Faux avis d'entreprise"
    },
    topics: {
      screenshotIphone: {
        title: "Comment faire une capture d'écran (iPhone)",
        steps: [
          "Regardez l'écran que vous voulez capturer.",
          "Appuyez en même temps sur le bouton latéral (côté droit) et le bouton Volume + (côté gauche).",
          "Relâchez vite. L'écran va flasher en blanc.",
          "L'image est enregistrée dans l'app Photos. Ouvrez Photos pour la trouver."
        ]
      },
      screenshotAndroid: {
        title: "Comment faire une capture d'écran (Android)",
        steps: [
          "Regardez l'écran que vous voulez capturer.",
          "Appuyez en même temps sur le bouton Marche/Arrêt et le bouton Volume -.",
          "Relâchez vite. Vous entendrez un clic ou verrez un flash.",
          "L'image est enregistrée dans votre app Photos ou Galerie."
        ]
      },
      facetime: {
        title: "Comment appeler votre famille en vidéo (iPhone)",
        steps: [
          "Ouvrez l'app FaceTime. C'est une icône verte avec une caméra vidéo blanche.",
          "Appuyez sur la personne à appeler dans vos contacts.",
          "Appuyez sur le bouton rond de la caméra vidéo (pas celui du téléphone).",
          "Attendez qu'ils répondent. Dites bonjour !",
          "Appuyez sur le bouton rouge pour raccrocher."
        ]
      },
      duo: {
        title: "Comment appeler votre famille en vidéo (Android)",
        steps: [
          "Ouvrez l'app Google Meet ou Duo.",
          "Appuyez sur Rechercher des contacts en haut.",
          "Choisissez la personne à appeler.",
          "Appuyez sur le bouton caméra vidéo.",
          "Attendez qu'ils répondent. Appuyez sur le bouton rouge pour raccrocher."
        ]
      },
      sendphoto: {
        title: "Comment envoyer une photo par message",
        steps: [
          "Ouvrez l'app Messages. C'est une icône verte avec une bulle blanche.",
          "Appuyez sur la conversation avec la personne destinataire.",
          "Appuyez sur l'icône caméra (📷) à côté de la zone de texte.",
          "Choisissez la photo dans votre pellicule.",
          "Appuyez sur la flèche bleue pour l'envoyer."
        ]
      },
      wifi: {
        title: "Comment se connecter au Wi-Fi",
        steps: [
          "Ouvrez Réglages. Cherchez une icône d'engrenage gris ⚙️ sur votre écran d'accueil.",
          "Appuyez sur Wi-Fi.",
          "Vous verrez une liste de réseaux. Appuyez sur votre réseau familial.",
          "Tapez le mot de passe. Il est Usually sur une étiquette de votre routeur.",
          "Appuyez sur Rejoindre ou Connecter. Vous êtes connecté quand vous voyez une coche bleue."
        ]
      },
      update: {
        title: "Comment mettre à jour votre téléphone",
        steps: [
          "Branchez votre téléphone sur un chargeur. Les mises à jour ont besoin d'énergie.",
          "Assurez-vous d'être connecté au Wi-Fi.",
          "Ouvrez Réglages ⚙️.",
          "Appuyez sur Général (iPhone) ou Système (Android).",
          "Appuyez sur Mise à jour logicielle.",
          "Appuyez sur Télécharger et installer. Attendez — ne débranchez pas ! Cela prend 15-30 minutes."
        ]
      },
      password: {
        title: "J'ai oublié mon mot de passe",
        steps: [
          "Sur l'écran qui demande votre mot de passe, cherchez \"Mot de passe oublié ?\"",
          "Appuyez dessus.",
          "Entrez votre email ou numéro de téléphone.",
          "Vérifiez vos emails ou SMS pour un code.",
          "Tapez le code.",
          "Créez un nouveau mot de passe dont vous vous souviendrez. Notez-le sur papier !"
        ]
      },
      textsize: {
        title: "Comment agrandir le texte",
        steps: [
          "Ouvrez Réglages ⚙️.",
          "Appuyez sur Luminosité et affichage (iPhone) ou Affichage (Android).",
          "Appuyez sur Taille du texte.",
          "Glissez le curseur vers la droite pour agrandir.",
          "Vous pouvez aussi activer \"Texte en gras\" pour mieux lire."
        ]
      },
      ringtone: {
        title: "Comment rendre mon téléphone plus fort",
        steps: [
          "Regardez le côté gauche de votre téléphone. Vous verrez deux boutons.",
          "Le bouton du hautmonte le volume. Celui du bas le baisse.",
          "Appuyez sur le bouton DU HAUT plusieurs fois jusqu'au volume maximum.",
          "Si c'est toujours bas, ouvrez Réglages ⚙️, puis Sons, et désactivez \"Mode silencieux\"."
        ]
      }
    },
    toast: {
      added: "Ajouté",
      removed: "Supprimé"
    },
    feedback: {
      prompt: "Comment ça va avec Buddy ?",
      easy: "Facile 👍",
      hard: "Difficile 👎",
      thanks: "Merci pour votre avis !",
      easyThanks: "Content de l'entendre !",
      hardSorry: "Désolé. Qu'est-ce qui a été dur ?",
      placeholder: "Qu'est-ce qui était confus ? (optionnel)",
      send: "Envoyer",
      skip: "Passer",
      sent: "✓ Merci !",
      shareTitle: "Vous connaissez quelqu'un à qui Buddy plairait ?",
      shareBody: "J'utilise Buddy — une appli simple pour les aînés. Appels en un clic, rappels de médicaments, détecteur d'arnaques. Gratuit, sans inscription.",
      shareButton: "Partager Buddy"
    }
  },

  /* ====================== GERMAN ====================== */
  de: {
    meta: {
      name: "German",
      nativeName: "Deutsch",
      code: "de",
      flag: "🇩🇪",
      dateLocale: "de-DE",
      emergencyNumber: "112"
    },
    app: {
      brandLine: "Dein Alltagshelfer",
      greeting: "Hallo, ich bin {name}",
      madeWith: "Mit Sorgfalt gemacht von"
    },
    time: {
      morning: "Guten Morgen ☀️",
      afternoon: "Guten Tag 🌤️",
      evening: "Guten Abend 🌙"
    },
    tiles: {
      people: { label: "Meine Leute", sub: "Familie & Freunde" },
      meds:  { label: "Medikamente", sub: "Erinnerungen" },
      notes: { label: "Meine Notizen", sub: "Erinnerungen und Notizen" },
      safety:{ label: "Sicherheit", sub: "Betrugsprüfung" },
      help:  { label: "Anleitungen", sub: "Schritt für Schritt" }
    },
    emergency: "Notfall — Zum Wählen der {number} antippen",
    upgrade: {
      title: "Buddy Plus",
      text: "— unbegrenzte Kontakte, Betrugsprüfung, Familienübersicht",
      button: "7 $/Monat",
      comingSoon: "Buddy Plus kommt bald",
      modalBody: "Hinterlassen Sie Ihre E-Mail und wir benachrichtigen Sie beim Start. Sie erhalten auch einen kostenlosen Leitfaden: \"5 Gespräche mit Ihrem älteren Elternteil über Online-Sicherheit.\"",
      emailLabel: "E-Mail",
      notNow: "Nicht jetzt",
      notify: "Benachrichtigen",
      badEmail: "Bitte geben Sie eine gültige E-Mail ein.",
      saved: "✓ Sie sind auf der Liste!"
    },
    checkin: {
      title: "Heutiger Check-in",
      empty: "Fügen Sie Ihre Medikamente hinzu, um sie zu verfolgen.",
      pending: "{n} Medikament{e} heute einzunehmen",
      partial: "{taken} von {total} heute eingenommen",
      done: "Alle {total} geschafft — gut gemacht! 🎉"
    },
    nav: {
      backHome: "← Zurück zum Start",
      backHelp: "← Zurück zu Anleitungen",
      backToHelp: "← Zurück zu Anleitungen",
      language: "Sprache"
    },
    people: {
      title: "Meine Leute",
      hint: "Tippen Sie auf **Anrufen**, um jemanden sofort anzurufen.",
      empty: "Noch keine Personen hinzugefügt. Tippen Sie unten auf \"+ Person hinzufügen\".",
      add: "+ Person hinzufügen",
      addTitle: "Person hinzufügen",
      delete: "×",
      removeConfirm: "{name} entfernen?"
    },
    meds: {
      title: "Meine Medikamente",
      hint: "Tippen Sie auf den grünen Kreis, wenn Sie ein Medikament einnehmen. Wird jeden Tag zurückgesetzt.",
      empty: "Noch keine Medikamente hinzugefügt. Tippen Sie unten auf \"+ Medikament hinzufügen\".",
      add: "+ Medikament hinzufügen",
      addTitle: "Medikament hinzufügen",
      taken: "✓ Eingenommen!",
      removeConfirm: "{name} entfernen?",
      alarm: "Erinnerung",
      alarmNotify: "⏰ Zeit für {name} ({time})"
    },
    notes: {
      title: "Meine Notizen",
      hint: "Schreiben Sie auf, was Sie sich merken möchten. Notizen mit einer Glocke senden Ihnen eine Erinnerung.",
      empty: "Noch keine Notizen. Tippen Sie auf \"+ Notiz hinzufügen\" unten.",
      add: "+ Notiz hinzufügen",
      addTitle: "Notiz hinzufügen",
      noteText: "Was möchten Sie sich merken?",
      placeholderNote: "z.B. Am Freitag die Bank anrufen, Einkaufen…",
      alarmTime: "Erinnerungszeit (optional)",
      alarmHint: "Buddy sendet Ihnen eine Benachrichtigung zu dieser Zeit. Leer lassen für keine Erinnerung.",
      noAlarm: "Keine Erinnerung",
      alarmNotify: "⏰ Erinnerung: {text}… ({time})",
      delete: "Notiz löschen",
      removeConfirm: "Diese Notiz löschen?"
    },
    onboarding: {
      welcomeTitle: "Willkommen bei Buddy!",
      welcomeText: "Buddy ist Ihr einfacher täglicher Helfer. Ich zeige Ihnen kurz alles.",
      peopleTitle: "Meine Leute",
      peopleText: "Fügen Sie Ihre Familie und Freunde hier hinzu. Dann können Sie sie mit einem Antippen anrufen.",
      medsTitle: "Medikamenten-Erinnerungen",
      medsText: "Fügen Sie Ihre Medikamente hinzu und tippen Sie auf den grünen Kreis. Sie können auch Alarme aktivieren.",
      safetyTitle: "Alles fertig!",
      safetyText: "Wenn Sie eine verdächtige Nachricht erhalten, nutzen Sie den Sicherheits-Checker. Der rote Notfall-Button ist immer da.",
      skip: "Überspringen",
      next: "Weiter",
      done: "Fertig ✓"
    },
    safety: {
      title: "Sicherheit",
      checkTitle: "Ist diese Nachricht ein Betrug?",
      checkHint: "Seltsame Nachricht erhalten? Hier einfügen und Buddy sucht nach Warnzeichen.",
      checkButton: "Diese Nachricht prüfen",
      placeholder: "Nachricht hier einfügen…",
      tooShort: "⚠️ Bitte die ganze Nachricht einfügen — ich brauche mindestens ein bis zwei Sätze.",
      clean: "✅ Ich sehe keine üblichen Warnzeichen. Das heißt nicht, dass es zu 100 % sicher ist — im Zweifel rufen Sie direkt an mit einer Nummer, die Sie selbst nachgeschlagen haben.",
      risky: "🚨 Das sieht riskant aus. Ich habe {n} Warnzeichen gefunden: {hits}. Klicken Sie keine Links an. Senden Sie kein Geld und keine Codes. Rufen Sie vorher jemanden an, dem Sie vertrauen.",
      trustedTitle: "Vertrauenswürdige Nummern",
      trustedHint: "Das sind die Menschen, denen Sie vertrauen. Wenn sie nach Geld fragen, prüfen Sie es, indem Sie sie unter einer bekannten Nummer zurückrufen.",
      emptyTrusted: "Fügen Sie vertrauenswürdige Personen unter \"Meine Leute\" hinzu.",
      call911: "🚨 {number} anrufen"
    },
    help: {
      title: "Wie Kann Ich Helfen?",
      hint: "Schritt-für-Schritt-Anleitungen für häufige Aufgaben am Telefon."
    },
    form: {
      name: "Name",
      phone: "Telefonnummer",
      relation: "In welcher Beziehung? (optional)",
      medTime: "Wann einnehmen",
      notes: "Notizen (optional)",
      email: "E-Mail",
      placeholderPersonName: "z. B. Sarah (Tochter)",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "z. B. Familie, Arzt, Nachbar",
      placeholderMedName: "z. B. Blutdrucktablette",
      placeholderMedTime: "z. B. Morgen, Mittag, Abend, Schlafenszeit",
      placeholderNotes: "z. B. Mit Essen",
      placeholderEmail: "sie@example.com",
      cancel: "Abbrechen",
      save: "Speichern",
      needName: "Bitte einen Namen eingeben.",
      needPhone: "Bitte eine Telefonnummer eingeben, damit Anrufen funktioniert."
    },
    scamPatterns: {
      urgency: "Zeitdruck",
      payment: "Ungewöhnliche Zahlung",
      authority: "Behörden-Imitation",
      verify: "Konto-Verifizierung",
      link: "Drängt zum Klick",
      prize: "Gewinn-Sprache",
      sensitive: "Fragt nach sensiblen Daten",
      familyEmergency: "Familien-Notfall-Betrug",
      threat: "Angstbasierte Drohungen",
      fakeCompany: "Falsche Firmenmitteilung"
    },
    topics: {
      screenshotIphone: {
        title: "Screenshot machen (iPhone)",
        steps: [
          "Schauen Sie auf den Bildschirm, den Sie aufnehmen wollen.",
          "Drücken Sie gleichzeitig die Seitentaste (rechts) und die Lauter-Taste (links).",
          "Lassen Sie schnell los. Der Bildschirm blinkt weiß.",
          "Das Bild ist in der Fotos-App gespeichert. Öffnen Sie Fotos, um es zu finden."
        ]
      },
      screenshotAndroid: {
        title: "Screenshot machen (Android)",
        steps: [
          "Schauen Sie auf den Bildschirm, den Sie aufnehmen wollen.",
          "Drücken Sie gleichzeitig die Power-Taste und die Leiser-Taste.",
          "Lassen Sie schnell los. Sie hören ein Klicken oder sehen ein Blitz.",
          "Das Bild ist in Ihrer Foto- oder Galerie-App gespeichert."
        ]
      },
      facetime: {
        title: "Videoanruf zur Familie (iPhone)",
        steps: [
          "Öffnen Sie die FaceTime-App. Grünes Symbol mit weißer Videokamera.",
          "Tippen Sie auf die Person, die Sie anrufen wollen.",
          "Tippen Sie auf den runden Videokamera-Button (nicht den Telefon-Button).",
          "Warten Sie, bis sie antworten. Winken Sie!",
          "Tippen Sie auf den roten Telefon-Button zum Auflegen."
        ]
      },
      duo: {
        title: "Videoanruf zur Familie (Android)",
        steps: [
          "Öffnen Sie die Google Meet- oder Duo-App.",
          "Tippen Sie oben auf Kontakte suchen.",
          "Wählen Sie die Person aus.",
          "Tippen Sie auf den Videokamera-Button.",
          "Warten Sie auf die Antwort. Roter Button zum Auflegen."
        ]
      },
      sendphoto: {
        title: "Ein Foto per Nachricht senden",
        steps: [
          "Öffnen Sie die Nachrichten-App. Grünes Symbol mit weißer Sprechblase.",
          "Tippen Sie auf die Unterhaltung mit der Person.",
          "Tippen Sie auf das Kamerasymbol (📷) neben dem Textfeld.",
          "Wählen Sie das gewünschte Foto aus.",
          "Tippen Sie auf den blauen Pfeil zum Senden."
        ]
      },
      wifi: {
        title: "Mit WLAN verbinden",
        steps: [
          "Öffnen Sie Einstellungen. Suchen Sie das graue Zahnrad ⚙️ auf dem Startbildschirm.",
          "Tippen Sie auf WLAN.",
          "Sie sehen eine Liste von Netzwerken. Tippen Sie auf Ihr Heimnetz.",
          "Geben Sie das Passwort ein. Steht Usually auf einem Aufkleber am Router.",
          "Tippen Sie auf Verbinden. Sie sind online, wenn Sie ein blaues Häkchen sehen."
        ]
      },
      update: {
        title: "Telefon aktualisieren",
        steps: [
          "Schließen Sie das Telefon an ein Ladegerät an.",
          "Stellen Sie sicher, dass Sie mit WLAN verbunden sind.",
          "Öffnen Sie Einstellungen ⚙️.",
          "Tippen Sie auf Allgemein (iPhone) oder System (Android).",
          "Tippen Sie auf Software-Update.",
          "Tippen Sie auf Herunterladen und installieren. Nicht ausstecken! Dauert 15-30 Minuten."
        ]
      },
      password: {
        title: "Passwort vergessen",
        steps: [
          "Suchen Sie auf dem Anmeldebildschirm \"Passwort vergessen?\"",
          "Tippen Sie darauf.",
          "Geben Sie Ihre E-Mail oder Telefonnummer ein.",
          "Schauen Sie in E-Mail oder SMS nach einem Code.",
          "Geben Sie den Code ein.",
          "Erstellen Sie ein neues Passwort. Schreiben Sie es auf Papier auf!"
        ]
      },
      textsize: {
        title: "Text größer machen",
        steps: [
          "Öffnen Sie Einstellungen ⚙️.",
          "Tippen Sie auf Anzeige & Helligkeit (iPhone) oder Anzeige (Android).",
          "Tippen Sie auf Textgröße.",
          "Ziehen Sie den Schieberegler nach rechts.",
          "Sie können auch \"Fetten Text\" aktivieren."
        ]
      },
      ringtone: {
        title: "Telefon lauter stellen",
        steps: [
          "Schauen Sie auf die linke Seite Ihres Telefons. Sie sehen zwei Tasten.",
          "Die obere Taste macht lauter. Die untere macht leiser.",
          "Drücken Sie die OBERE Taste oft, bis die Lautstärke oben ist.",
          "Wenn es noch leise ist: Einstellungen ⚙️, dann Töne, und \"Stumm\" ausschalten."
        ]
      }
    },
    toast: {
      added: "Hinzugefügt",
      removed: "Entfernt"
    },
    feedback: {
      prompt: "Wie klappt es mit Buddy?",
      easy: "Einfach 👍",
      hard: "Schwer 👎",
      thanks: "Danke für Ihr Feedback!",
      easyThanks: "Freut mich!",
      hardSorry: "Entschuldigung. Was war schwer?",
      placeholder: "Was war unklar? (optional)",
      send: "Senden",
      skip: "Überspringen",
      sent: "✓ Danke!",
      shareTitle: "Kennst du jemanden, dem Buddy gefallen würde?",
      shareBody: "Ich benutze Buddy — eine einfache App für ältere Familienmitglieder. Anrufe mit einem Tipp, Medikamenten-Erinnerungen, Betrugsprüfung. Kostenlos, ohne Anmeldung.",
      shareButton: "Buddy teilen"
    }
  },

  /* ====================== PORTUGUESE (BR) ====================== */
  pt: {
    meta: {
      name: "Portuguese",
      nativeName: "Português",
      code: "pt",
      flag: "🇧🇷",
      dateLocale: "pt-BR",
      emergencyNumber: "190"
    },
    app: {
      brandLine: "Seu ajudante do dia a dia",
      greeting: "Olá, eu sou {name}",
      madeWith: "Feito com carinho por"
    },
    time: {
      morning: "Bom dia ☀️",
      afternoon: "Boa tarde 🌤️",
      evening: "Boa noite 🌙"
    },
    tiles: {
      people: { label: "Minhas Pessoas", sub: "Família e amigos" },
      meds:  { label: "Remédios", sub: "Lembretes e checks" },
      notes: { label: "Minhas Notas", sub: "Lembretes e anotações" },
      safety:{ label: "Segurança", sub: "Detector de golpes" },
      help:  { label: "Como Fazer", sub: "Guias passo a passo" }
    },
    emergency: "Emergência — Toque para Ligar {number}",
    upgrade: {
      title: "Buddy Plus",
      text: "— contatos ilimitados, detector de golpes, painel familiar",
      button: "$7/mês",
      comingSoon: "Buddy Plus em breve",
      modalBody: "Deixe seu email e avisamos quando lançar. Também enviaremos um guia grátis: \"5 Conversas Para Ter Com Seu Pai Idoso Sobre Segurança Online.\"",
      emailLabel: "Email",
      notNow: "Agora não",
      notify: "Avise-me",
      badEmail: "Por favor, insira um email válido.",
      saved: "✓ Você está na lista!"
    },
    checkin: {
      title: "Check-in de Hoje",
      empty: "Adicione seus remédios para acompanhar.",
      pending: "{n} remédio{s} para tomar hoje",
      partial: "{taken} de {total} tomados hoje",
      done: "Todos os {total} prontos — muito bem! 🎉"
    },
    nav: {
      backHome: "← Voltar ao Início",
      backHelp: "← Voltar a Como Fazer",
      backToHelp: "← Voltar a Como Fazer",
      language: "Idioma"
    },
    people: {
      title: "Minhas Pessoas",
      hint: "Toque em **Ligar** para ligar alguém agora.",
      empty: "Nenhuma pessoa adicionada. Toque em \"+ Adicionar Pessoa\" abaixo.",
      add: "+ Adicionar Pessoa",
      addTitle: "Adicionar Pessoa",
      delete: "×",
      removeConfirm: "Remover {name}?"
    },
    meds: {
      title: "Meus Remédios",
      hint: "Toque no círculo verde quando tomar um remédio. Reseta todo dia.",
      empty: "Nenhum remédio adicionado. Toque em \"+ Adicionar Remédio\" abaixo.",
      add: "+ Adicionar Remédio",
      addTitle: "Adicionar Remédio",
      taken: "✓ Tomado!",
      removeConfirm: "Remover {name}?",
      alarm: "Alarme",
      alarmNotify: "⏰ Hora de tomar {name} ({time})"
    },
    notes: {
      title: "Minhas Notas",
      hint: "Escreva o que quiser lembrar. Notas com sino enviarão um lembrete.",
      empty: "Sem notas ainda. Toque em \"+ Adicionar nota\" abaixo.",
      add: "+ Adicionar nota",
      addTitle: "Adicionar nota",
      noteText: "O que quer lembrar?",
      placeholderNote: "ex. Ligar para o banco sexta, buscar compras…",
      alarmTime: "Hora do lembrete (opcional)",
      alarmHint: "Buddy enviará uma notificação neste horário. Deixe vazio para sem lembrete.",
      noAlarm: "Sem lembrete",
      alarmNotify: "⏰ Lembrete: {text}… ({time})",
      delete: "Apagar nota",
      removeConfirm: "Apagar esta nota?"
    },
    onboarding: {
      welcomeTitle: "Bem-vindo ao Buddy!",
      welcomeText: "Buddy é seu ajudante diário simples. Deixe-me mostrar — só leva um momento.",
      peopleTitle: "Meus Contatos",
      peopleText: "Adicione família e amigos aqui. Depois é só tocar para ligar.",
      medsTitle: "Lembretes de remédios",
      medsText: "Adicione seus remédios e toque no círculo verde ao tomar. Também pode ativar alarmes.",
      safetyTitle: "Tudo pronto!",
      safetyText: "Se receber uma mensagem suspeita, use o verificador de segurança. E o botão vermelho de emergência está sempre ali.",
      skip: "Pular",
      next: "Próximo",
      done: "Pronto ✓"
    },
    safety: {
      title: "Segurança",
      checkTitle: "Esta mensagem é um golpe?",
      checkHint: "Recebeu uma mensagem estranha? Cole aqui e Buddy procura os sinais de alerta.",
      checkButton: "Verificar Esta Mensagem",
      placeholder: "Cole a mensagem aqui…",
      tooShort: "⚠️ Cole a mensagem completa — preciso de pelo menos uma ou duas frases para checar.",
      clean: "✅ Não vejo os sinais de alerta comuns. Isso não significa 100% seguro — na dúvida, ligue diretamente usando um número que você mesmo procurar.",
      risky: "🚨 Isso parece arriscado. Encontrei {n} sinal{s} de alerta: {hits}. Não clique em links. Não envie dinheiro nem códigos. Ligue para alguém de confiança antes de agir.",
      trustedTitle: "Números de Confiança",
      trustedHint: "Estas são as pessoas em quem você confia. Se pedirem dinheiro, confirme ligando de volta para um número que você já conhece.",
      emptyTrusted: "Adicione pessoas de confiança em \"Minhas Pessoas\" no início.",
      call911: "🚨 Ligar {number}"
    },
    help: {
      title: "Como Posso Ajudar?",
      hint: "Guias passo a passo para tarefas comuns do celular."
    },
    form: {
      name: "Nome",
      phone: "Número de telefone",
      relation: "Qual a relação? (opcional)",
      medTime: "Quando tomar",
      notes: "Notas (opcional)",
      email: "Email",
      placeholderPersonName: "ex. Carla (filha)",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "ex. Família, Médico, Vizinho",
      placeholderMedName: "ex. Remédio de pressão",
      placeholderMedTime: "ex. Manhã, Meio-dia, Noite, Dormir",
      placeholderNotes: "ex. Com comida",
      placeholderEmail: "voce@email.com",
      cancel: "Cancelar",
      save: "Salvar",
      needName: "Por favor, insira um nome.",
      needPhone: "Por favor, insira um telefone para o botão Ligar funcionar."
    },
    scamPatterns: {
      urgency: "Pressão de urgência",
      payment: "Pagamento incomum",
      authority: "Falsificação de autoridade",
      verify: "Pedido de verificar conta",
      link: "Empurra para clicar link",
      prize: "Linguagem de prêmio",
      sensitive: "Pede informação sensível",
      familyEmergency: "Golpe de emergência familiar",
      threat: "Ameaças com medo",
      fakeCompany: "Aviso falso de empresa"
    },
    topics: {
      screenshotIphone: {
        title: "Como tirar print (iPhone)",
        steps: [
          "Olhe para a tela que quer capturar.",
          "Aperte o botão lateral (lado direito) e o botão de Aumentar Volume (lado esquerdo) AO MESMO TEMPO.",
          "Solte rápido. A tela vai piscar em branco.",
          "A foto foi salva no app Fotos. Abra Fotos para encontrar."
        ]
      },
      screenshotAndroid: {
        title: "Como tirar print (Android)",
        steps: [
          "Olhe para a tela que quer capturar.",
          "Aperte o botão de Energia e o botão de Diminuir Volume AO MESMO TEMPO.",
          "Solte rápido. Você vai ouvir um clique ou ver um flash.",
          "A foto foi salva no app Fotos ou Galeria."
        ]
      },
      facetime: {
        title: "Como fazer videochamada para família (iPhone)",
        steps: [
          "Abra o app FaceTime. Ícone verde com uma câmera de vídeo branca.",
          "Toque na pessoa que quer ligar.",
          "Toque no botão redondo da câmera de vídeo (não o do telefone).",
          "Espere atender. Acene oi!",
          "Toque no botão vermelho para desligar."
        ]
      },
      duo: {
        title: "Como fazer videochamada para família (Android)",
        steps: [
          "Abra o app Google Meet ou Duo.",
          "Toque em Procurar contatos no topo.",
          "Escolha a pessoa para ligar.",
          "Toque no botão da câmera de vídeo.",
          "Espere atender. Toque no botão vermelho para desligar."
        ]
      },
      sendphoto: {
        title: "Como mandar foto por mensagem",
        steps: [
          "Abra o app Mensagens. Ícone verde com balão branco.",
          "Toque na conversa com a pessoa.",
          "Toque no ícone da câmera (📷) ao lado do campo de texto.",
          "Escolha a foto no rolo da câmera.",
          "Toque na seta azul para enviar."
        ]
      },
      wifi: {
        title: "Como conectar ao Wi-Fi",
        steps: [
          "Abra Ajustes. Procure o ícone cinza de engrenagem ⚙️.",
          "Toque em Wi-Fi.",
          "Você verá uma lista de redes. Toque na sua rede de casa.",
          "Digite a senha. Geralmente fica numa etiqueta no roteador.",
          "Toque em Entrar ou Conectar. Você está online quando aparecer um ✓ azul."
        ]
      },
      update: {
        title: "Como atualizar o celular",
        steps: [
          "Conecte o celular no carregador. Atualizações precisam de energia.",
          "Confirme que está no Wi-Fi.",
          "Abra Ajustes ⚙️.",
          "Toque em Geral (iPhone) ou Sistema (Android).",
          "Toque em Atualização de Software.",
          "Toque em Baixar e Instalar. Espere — não desconecte! Leva 15-30 min."
        ]
      },
      password: {
        title: "Esqueci minha senha",
        steps: [
          "Na tela que pede senha, procure \"Esqueceu a senha?\"",
          "Toque nela.",
          "Digite seu email ou telefone.",
          "Olhe seu email ou SMS para pegar o código.",
          "Digite o código.",
          "Crie uma senha nova que você vá lembrar. Anote no papel!"
        ]
      },
      textsize: {
        title: "Como aumentar o texto",
        steps: [
          "Abra Ajustes ⚙️.",
          "Toque em Tela e Brilho (iPhone) ou Tela (Android).",
          "Toque em Tamanho do Texto.",
          "Arraste o controle para a direita.",
          "Você também pode ativar \"Texto em Negrito\"."
        ]
      },
      ringtone: {
        title: "Como deixar o celular mais alto",
        steps: [
          "Olhe no lado esquerdo do celular. Há dois botões.",
          "O botão de cima aumenta o volume. O de baixo abaixa.",
          "Aperte o de CIMA várias vezes até o volume máximo.",
          "Se ainda estiver baixo: Ajustes ⚙️, depois Sons, e desligue \"Modo Silencioso\"."
        ]
      }
    },
    toast: {
      added: "Adicionado",
      removed: "Removido"
    },
    feedback: {
      prompt: "Como está sendo usar o Buddy?",
      easy: "Fácil 👍",
      hard: "Difícil 👎",
      thanks: "Obrigado pelo feedback!",
      easyThanks: "Que bom!",
      hardSorry: "Desculpa. O que foi difícil?",
      placeholder: "O que foi confuso? (opcional)",
      send: "Enviar",
      skip: "Pular",
      sent: "✓ Obrigado!",
      shareTitle: "Conhece alguém que gostaria do Buddy?",
      shareBody: "Estou usando o Buddy — um app simples para familiares mais velhos. Ligação com um toque, lembretes de remédios, detector de golpes. Grátis, sem cadastro.",
      shareButton: "Compartilhar Buddy"
    }
  },

  /* ====================== CHINESE (Simplified) ====================== */
  zh: {
    meta: {
      name: "Chinese",
      nativeName: "中文",
      code: "zh",
      flag: "🇨🇳",
      dateLocale: "zh-CN",
      emergencyNumber: "110"
    },
    app: {
      brandLine: "您的日常小帮手",
      greeting: "您好，我是{name}",
      madeWith: "用心制作，由"
    },
    time: {
      morning: "早上好 ☀️",
      afternoon: "下午好 🌤️",
      evening: "晚上好 🌙"
    },
    tiles: {
      people: { label: "我的家人", sub: "家人和朋友" },
      meds:  { label: "我的药品", sub: "提醒和打卡" },
      notes: { label: "我的备忘", sub: "提醒和笔记" },
      safety:{ label: "安全中心", sub: "识别诈骗电话" },
      help:  { label: "使用教程", sub: "一步步教您" }
    },
    emergency: "紧急情况 — 点击拨打 {number}",
    upgrade: {
      title: "Buddy 高级版",
      text: "— 无限联系人、诈骗识别、家庭面板",
      button: "每月 7 美元",
      comingSoon: "Buddy 高级版即将推出",
      modalBody: "留下您的邮箱，我们会在上线时通知您。还会送您一份免费指南：《与父母谈网络安全的 5 个话题》。",
      emailLabel: "邮箱",
      notNow: "暂不",
      notify: "通知我",
      badEmail: "请输入有效的邮箱。",
      saved: "✓ 已加入列表！"
    },
    checkin: {
      title: "今日打卡",
      empty: "添加您的药品来追踪。",
      pending: "今天还有 {n} 种药要吃",
      partial: "今天已吃 {taken}/{total}",
      done: "今天 {total} 种药都吃完了，做得好！🎉"
    },
    nav: {
      backHome: "← 返回首页",
      backHelp: "← 返回教程",
      backToHelp: "← 返回教程",
      language: "语言"
    },
    people: {
      title: "我的家人",
      hint: "点 **拨打** 立即联系对方。",
      empty: "还没有添加联系人。点击下方的 \"+ 添加联系人\"。",
      add: "+ 添加联系人",
      addTitle: "添加联系人",
      delete: "×",
      removeConfirm: "删除 {name}？"
    },
    meds: {
      title: "我的药品",
      hint: "吃完药后点绿色圆圈打卡。每天自动重置。",
      empty: "还没有添加药品。点击下方的 \"+ 添加药品\"。",
      add: "+ 添加药品",
      addTitle: "添加药品",
      taken: "✓ 已吃！",
      removeConfirm: "删除 {name}？",
      alarm: "提醒",
      alarmNotify: "⏰ 该吃{name}了（{time}）"
    },
    notes: {
      title: "我的备忘",
      hint: "写下任何想记住的事。带铃铛的备忘会发送提醒。",
      empty: "还没有备忘。点击下方的\"+ 添加备忘\"。",
      add: "+ 添加备忘",
      addTitle: "添加备忘",
      noteText: "想记住什么？",
      placeholderNote: "例如：周五给银行打电话，去买菜…",
      alarmTime: "提醒时间（可选）",
      alarmHint: "Buddy会在这个时间发送通知。留空则不提醒。",
      noAlarm: "无提醒",
      alarmNotify: "⏰ 提醒：{text}…（{time}）",
      delete: "删除备忘",
      removeConfirm: "删除这条备忘吗？"
    },
    onboarding: {
      welcomeTitle: "欢迎使用Buddy！",
      welcomeText: "Buddy是您的简单日常助手。让我带您看看——只需一会儿。",
      peopleTitle: "我的人",
      peopleText: "在这里添加家人和朋友。然后只需点一下就能打电话。",
      medsTitle: "药物提醒",
      medsText: "添加您的药物，吃药时点击绿色圆圈。还可以开启提醒——Buddy会通知您。",
      safetyTitle: "一切就绪！",
      safetyText: "如果您收到可疑消息，请使用安全检查器。红色紧急按钮始终在那里。",
      skip: "跳过",
      next: "下一步",
      done: "完成 ✓"
    },
    safety: {
      title: "安全中心",
      checkTitle: "这条消息是不是诈骗？",
      checkHint: "收到奇怪的消息？把它粘贴到这里，Buddy 会帮您找警告信号。",
      checkButton: "检查这条消息",
      placeholder: "在这里粘贴消息…",
      tooShort: "⚠️ 请粘贴完整消息 — 我至少需要一两句话。",
      clean: "✅ 我没看到常见的诈骗信号。但不代表 100% 安全 — 如有疑问，请用您自己查到的电话号码直接拨打。",
      risky: "🚨 这看起来有风险。我发现了 {n} 个警告信号：{hits}。不要点击链接。不要转账或发送验证码。先打电话给您信任的人。",
      trustedTitle: "可信电话",
      trustedHint: "这些都是您信任的人。如果他们要钱，请用您已知的号码回拨确认。",
      emptyTrusted: "请到首页的 \"我的家人\" 添加可信任的联系人。",
      call911: "🚨 拨打 {number}"
    },
    help: {
      title: "我能帮您做什么？",
      hint: "手机常见操作的一步步教程。"
    },
    form: {
      name: "姓名",
      phone: "电话号码",
      relation: "关系（可选）",
      medTime: "什么时候吃",
      notes: "备注（可选）",
      email: "邮箱",
      placeholderPersonName: "例：小张（女儿）",
      placeholderPhone: "555-123-4567",
      placeholderRelation: "例：家人、医生、邻居",
      placeholderMedName: "例：降压药",
      placeholderMedTime: "例：早上、中午、晚上、睡前",
      placeholderNotes: "例：饭后吃",
      placeholderEmail: "you@example.com",
      cancel: "取消",
      save: "保存",
      needName: "请输入姓名。",
      needPhone: "请输入电话号码，否则拨打按钮没法用。"
    },
    scamPatterns: {
      urgency: "紧迫感压力",
      payment: "异常付款方式",
      authority: "冒充权威",
      verify: "要求验证账户",
      link: "催促点击链接",
      prize: "中奖话术",
      sensitive: "索要敏感信息",
      familyEmergency: "家人紧急骗局",
      threat: "恐吓威胁",
      fakeCompany: "假冒公司通知"
    },
    topics: {
      screenshotIphone: {
        title: "如何截图（iPhone）",
        steps: [
          "看您想截图的屏幕。",
          "同时按下侧边按钮（右边）和音量上键（左边）。",
          "快速松开。屏幕会闪一下白色。",
          "图片已保存在相册里。打开相册就能找到。"
        ]
      },
      screenshotAndroid: {
        title: "如何截图（安卓）",
        steps: [
          "看您想截图的屏幕。",
          "同时按下电源键和音量下键。",
          "快速松开。会听到咔哒声或看到闪光。",
          "图片已保存在相册或图库里。"
        ]
      },
      facetime: {
        title: "如何给家人打视频电话（iPhone）",
        steps: [
          "打开 FaceTime。绿色图标，白色摄像头。",
          "在通讯录里点您想联系的人。",
          "点圆形的视频按钮（不是电话那个）。",
          "等对方接听，挥挥手打招呼！",
          "挂断时点红色电话按钮。"
        ]
      },
      duo: {
        title: "如何给家人打视频电话（安卓）",
        steps: [
          "打开 Google Meet 或 Duo。",
          "点顶部的搜索联系人。",
          "选择您想联系的人。",
          "点视频按钮。",
          "等对方接听。点红色按钮挂断。"
        ]
      },
      sendphoto: {
        title: "如何用短信发照片",
        steps: [
          "打开信息 App。绿色图标，白色对话气泡。",
          "点您想发给谁的对话。",
          "点输入框旁边的相机图标（📷）。",
          "从相册选一张照片。",
          "点蓝色箭头发送。"
        ]
      },
      wifi: {
        title: "如何连接 Wi-Fi",
        steps: [
          "打开设置。在主屏幕找灰色的齿轮 ⚙️ 图标。",
          "点 Wi-Fi。",
          "会看到网络列表。点您家里的网络。",
          "输入密码。一般贴在路由器的标签上。",
          "点加入或连接。看到蓝色对勾就是连上了。"
        ]
      },
      update: {
        title: "如何更新手机",
        steps: [
          "把手机插上充电器。更新需要电。",
          "确保连上 Wi-Fi。",
          "打开设置 ⚙️。",
          "点通用（iPhone）或系统（安卓）。",
          "点软件更新。",
          "点下载并安装。等等 — 别拔充电器！需要 15-30 分钟。"
        ]
      },
      password: {
        title: "我忘了密码",
        steps: [
          "在需要输密码的页面，找 \"忘记密码？\"",
          "点它。",
          "输入您的邮箱或手机号。",
          "看邮箱或短信里的验证码。",
          "输入验证码。",
          "设一个新密码。写在纸上保存好！"
        ]
      },
      textsize: {
        title: "如何把字变大",
        steps: [
          "打开设置 ⚙️。",
          "点显示与亮度（iPhone）或显示（安卓）。",
          "点文字大小。",
          "把滑块向右拖，字就变大了。",
          "您也可以打开 \"粗体文字\"。"
        ]
      },
      ringtone: {
        title: "如何让手机声音更大",
        steps: [
          "看手机左侧，会看到两个按钮。",
          "上面的按钮是音量上键，下面是音量下键。",
          "多按上面的按钮，直到音量最大。",
          "如果还小：打开设置 ⚙️，点声音，关掉 \"静音模式\"。"
        ]
      }
    },
    toast: {
      added: "已添加",
      removed: "已删除"
    },
    feedback: {
      prompt: "Buddy 用得怎么样？",
      easy: "简单 👍",
      hard: "困难 👎",
      thanks: "感谢您的反馈！",
      easyThanks: "很高兴听您这么说！",
      hardSorry: "抱歉。是哪里让您觉得难？",
      placeholder: "哪里不清楚？（可选）",
      send: "发送",
      skip: "跳过",
      sent: "✓ 谢谢！",
      shareTitle: "有朋友会喜欢 Buddy 吗？",
      shareBody: "我在用 Buddy — 一个为长辈设计的简单 App。一键拨号、吃药提醒、诈骗识别。免费，无需注册。",
      shareButton: "分享 Buddy"
    }
  },

/* ====================== FINNISH ====================== */
  fi: {
    meta: {
      name: "Finnish",
      nativeName: "Suomi",
      code: "fi",
      flag: "🇫🇮",
      dateLocale: "fi-FI",
      emergencyNumber: "112"
    },
    app: {
      brandLine: "Päivittäinen apurisi",
      greeting: "Hei, olen {name}",
      madeWith: "Tehty sydämellä:"
    },
    time: {
      morning: "Hyvää huomenta ☀️",
      afternoon: "Hyvää iltapäivää 🌤️",
      evening: "Hyvää iltaa 🌙"
    },
    tiles: {
      people: { label: "Läheiseni", sub: "Perhe ja ystävät" },
      meds:  { label: "Lääkkeet", sub: "Muistutukset ja merkinnät" },
      notes: { label: "Muistiinpanot", sub: "Muistutukset ja viestit" },
      safety:{ label: "Turvassa", sub: "Huijauksen tunnistus" },
      help:  { label: "Ohjeet", sub: "Vaiheittaiset oppaat" }
    },
    emergency: "Hätänumero — Soita {number} painamalla",
    upgrade: {
      title: "Buddy Plus",
      text: "— rajoittamattomat yhteystiedot, huijaustunnistus, perhepaneeli",
      button: "7 $/kk",
      comingSoon: "Buddy Plus tulossa pian",
      modalBody: "Jätä sähköpostisi, niin ilmoitamme julkaisusta. Saat myös ilmaisen oppaan: \"5 keskustelua vanhemman kanssa verkkoturvallisuudesta.\"",
      emailLabel: "Sähköposti",
      notNow: "Ei nyt",
      notify: "Ilmoita minulle",
      badEmail: "Anna kelvollinen sähköposti.",
      saved: "✓ Olet listalla!"
    },
    checkin: {
      title: "Päivän kuittaus",
      empty: "Lisää lääkkeet seurantaa varten.",
      pending: "{n} lääkettä otettavana tänään",
      partial: "{taken}/{total} otettu tänään",
      done: "Kaikki {total} otettu — hienoa! 🎉"
    },
    nav: {
      backHome: "← Takaisin etusivulle",
      backHelp: "← Takaisin ohjeisiin",
      backToHelp: "← Takaisin ohjeisiin",
      language: "Kieli"
    },
    people: {
      title: "Läheiseni",
      hint: "Paina **Soita** soittaaksesi heti.",
      empty: "Ei lisättyjä henkilöitä. Paina \"+ Lisää henkilö\" alla.",
      add: "+ Lisää henkilö",
      addTitle: "Lisää henkilö",
      delete: "×",
      removeConfirm: "Poistetaanko {name}?"
    },
    meds: {
      title: "Lääkkeeni",
      hint: "Paina vihreää ympyrää kun otat lääkkeen. Nollautuu päivittäin.",
      empty: "Ei lisättyjä lääkkeitä. Paina \"+ Lisää lääke\" alla.",
      add: "+ Lisää lääke",
      addTitle: "Lisää lääke",
      taken: "✓ Otettu!",
      removeConfirm: "Poistetaanko {name}?",
      alarm: "Hälytys",
      alarmNotify: "⏰ On aika ottaa {name} ({time})"
    },
    notes: {
      title: "Muistiinpanot",
      hint: "Kirjoita ylös mitä tahansa. Muistiinpanoihin, joissa on kello, saat muistutuksen.",
      empty: "Ei muistiinpanoja vielä. Paina \"+ Lisää muistiinpano\" alla.",
      add: "+ Lisää muistiinpano",
      addTitle: "Lisää muistiinpano",
      noteText: "Mitä haluat muistaa?",
      placeholderNote: "esim. Soita pankille perjantaina, nouda ruokaa…",
      alarmTime: "Muistutusaika (valinnainen)",
      alarmHint: "Buddy lähettää ilmoituksen tässä ajassa. Jätä tyhjäksi ilman muistutusta.",
      noAlarm: "Ei muistutusta",
      alarmNotify: "⏰ Muistutus: {text}… ({time})",
      delete: "Poista muistiinpano",
      removeConfirm: "Poistetaanko tämä muistiinpano?"
    },
    onboarding: {
      welcomeTitle: "Tervetuloa Buddyyn!",
      welcomeText: "Buddy on yksinkertainen päivittäinen apurisi. Käyn läpi asiat hetkessä.",
      peopleTitle: "Läheiseni",
      peopleText: "Lisää perheesi ja ystäväsi tänne. Sitten voit soittaa heille yhdellä painalluksella — ei tarvitse etsiä yhteystietoja.",
      medsTitle: "Lääkemuisoitukset",
      medsText: "Lisää lääkkeesi ja paina vihreää ympyrää kun otat ne. Voit myös laittaa hälytykset päälle — Buddy muistuttaa kun on aika.",
      safetyTitle: "Kaikki valmista!",
      safetyText: "Jos saat epäilyttävän viestin, käytä Turvassa-tarkistinta. Punainen hätäpainike on aina tarvittaessa. Paina Valmis aloittaaksesi!",
      skip: "Ohita",
      next: "Seuraava",
      done: "Valmis ✓"
    },
    safety: {
      title: "Turvassa",
      checkTitle: "Onko tämä viesti huijaus?",
      checkHint: "Saitko oudon viestin? Liitä se tähän, niin Buddy etsii varoitusmerkkejä.",
      checkButton: "Tarkista viesti",
      placeholder: "Liitä viesti tähän…",
      tooShort: "⚠️ Liitä koko viesti — tarvitsen ainakin yhden tai kaksi lausetta.",
      clean: "✅ En näe tavallisia varoitusmerkkejä. Se ei tarkoita 100 %:n turvallisuutta — epäselvissä tapauksissa soita suoraan numeroon, jonka olet itse hakenut.",
      risky: "🚨 Tämä vaikuttaa riskialttiilta. Löysin {n} mahdollista vaaraa: {hits}. Älä klikkaa linkkejä. Älä lähetä rahaa tai koodeja. Soita luotetulle henkilölle ennen toimimista.",
      trustedTitle: "Luotetut numerot",
      trustedHint: "Nämä ovat henkilöitä, joihin luotat. Jos he pyytävät rahaa, varmista soittamalla takaisin numeroon, jonka tiedät.",
      emptyTrusted: "Lisää luotettuja henkilöitä etusivun \"Läheiseni\"-kohdassa.",
      call911: "🚨 Soita {number}"
    },
    help: {
      title: "Miten Voin Auttaa?",
      hint: "Vaiheittaisia ohjeita yleisiin puhelintoimintoihin."
    },
    form: {
      name: "Nimi",
      phone: "Puhelinnumero",
      relation: "Suhde (valinnainen)",
      medTime: "Milloin otetaan",
      notes: "Muistiinpanot (valinnainen)",
      email: "Sähköposti",
      placeholderPersonName: "esim. Sari (tytär)",
      placeholderPhone: "040-1234567",
      placeholderRelation: "esim. Perhe, Lääkäri, Naapuri",
      placeholderMedName: "esim. Verenpainelääke",
      placeholderMedTime: "esim. Aamu, Keskipäivä, Ilta, Nukkumaan mennessä",
      placeholderNotes: "esim. Ruuan kanssa",
      placeholderEmail: "sinä@esimerkki.fi",
      cancel: "Peruuta",
      save: "Tallenna",
      needName: "Anna nimi.",
      needPhone: "Anna puhelinnumero, jotta Soita-painike toimii."
    },
    scamPatterns: {
      urgency: "Kiireen painostus",
      payment: "Epätavallinen maksutapa",
      authority: "Viranomaisen esiintyminen",
      verify: "Tilin vahvistuspyyntö",
      link: "Painostaa klikkaamaan linkkiä",
      prize: "Palkinto/palkintojargon",
      sensitive: "Pyytää arkaluonteisia tietoja",
      familyEmergency: "Perheen hätäviesti-huijaus",
      threat: "Pelotteluuhkaukset",
      fakeCompany: "Valeyritysilmoitus"
    },
    topics: {
      screenshotIphone: {
        title: "Kuvakaappauksen ottaminen (iPhone)",
        steps: [
          "Katso näyttöä, jonka haluat kaapata.",
          "Paina samanaikaisesti sivupainiketta (oikea reuna) ja äänenvoimakkuuden ylös -painiketta (vasen reuna).",
          "Päästä irti nopeasti. Näyttö välähtää valkoisena.",
          "Kuva tallentuu Kuvat-sovellukseen. Avaa Kuvat löytääksesi sen."
        ]
      },
      screenshotAndroid: {
        title: "Kuvakaappauksen ottaminen (Android)",
        steps: [
          "Katso näyttöä, jonka haluat kaapata.",
          "Paina samanaikaisesti virtapainiketta ja äänenvoimakkuuden alas -painiketta.",
          "Päästä irti nopeasti. Kuulet napsahduksen tai näet välähdyksen.",
          "Kuva tallentuu Kuvat- tai Galleria-sovellukseen."
        ]
      },
      facetime: {
        title: "Videopuhelu perheelle (iPhone)",
        steps: [
          "Avaa FaceTime-sovellus. Vihreä kuvake, jossa valkoinen videokamera.",
          "Napauta yhteystiedoista henkilöä, jolle haluat soittaa.",
          "Napauta pyöreää videokameran painiketta (ei puhelinpainiketta).",
          "Odota vastausta. Heitä!",
          "Napauta punaista puhelinpainiketta lopettaaksesi."
        ]
      },
      duo: {
        title: "Videopuhelu perheelle (Android)",
        steps: [
          "Avaa Google Meet- tai Duo-sovellus.",
          "Napauta Etsi yhteystietoja ylhäällä.",
          "Valitse henkilö, jolle haluat soittaa.",
          "Napauta videokameran painiketta.",
          "Odota vastausta. Napauta punaista painiketta lopettaaksesi."
        ]
      },
      sendphoto: {
        title: "Kuvan lähettäminen tekstiviestillä",
        steps: [
          "Avaa Viestit-sovellus. Vihreä kuvake, jossa valkoinen puhekupla.",
          "Napauta keskustelua henkilön kanssa.",
          "Napauta kamerakuvaketta (📷) kirjoitusalueen vieressä.",
          "Valitse kuva kamerakierrosta.",
          "Napauta sinistä nuolta lähettääksesi."
        ]
      },
      wifi: {
        title: "Wi-Fi-verkkoon yhdistäminen",
        steps: [
          "Avaa Asetukset. Etsi harmaa rataskuvake ⚙️ aloitusnäytöltä.",
          "Napauta Wi-Fi.",
          "Näet verkkoluettelon. Napauta kotiverkkoasi.",
          "Anna salasana. Se on yleensä tarrassa reitittimessä.",
          "Napauta Liity tai Yhdistä. Olet verkossa, kun näet sinisen valintamerkin."
        ]
      },
      update: {
        title: "Puhelimen päivittäminen",
        steps: [
          "Liitä puhelin laturiin. Päivitykset tarvitsevat virtaa.",
          "Varmista, että olet yhdistetty Wi-Fi-verkkoon.",
          "Avaa Asetukset ⚙️.",
          "Napauta Yleiset (iPhone) tai Järjestelmä (Android).",
          "Napauta Ohjelmistopäivitys.",
          "Napauta Lataa ja asenna. Odota — älä irrota! Kestää 15-30 minuuttia."
        ]
      },
      password: {
        title: "Unohdin salasanani",
        steps: [
          "Etsi salasananäytöltä \"Unohditko salasanan?\"",
          "Napauta sitä.",
          "Anna sähköpostisi tai puhelinnumerosi.",
          "Tarkista sähköposti tai tekstiviestit koodin varalta.",
          "Anna koodi.",
          "Luo uusi salasana, jonka muistat. Kirjoita se paperille!"
        ]
      },
      textsize: {
        title: "Tekstin suurentaminen",
        steps: [
          "Avaa Asetukset ⚙️.",
          "Napauta Näyttö ja kirkkaus (iPhone) tai Näyttö (Android).",
          "Napauta Tekstin koko.",
          "Vedä liukusäädintä oikealle suurentaaksesi tekstiä.",
          "Voit myös ottaa käyttöön \"Lihavoitu teksti\" -asetuksen."
        ]
      },
      ringtone: {
        title: "Puhelimen soittoäänen voimistaminen",
        steps: [
          "Katso puhelimen vasenta reunaa. Näet kaksi painiketta.",
          "Yläpainike voimistaa ääntä. Alapainike hiljentää.",
          "Paina YLÄPAINIKETTA monta kertaa, kunnes äänenvoimakkuus on maksimissa.",
          "Jos se on yhä hiljainen: avaa Asetukset ⚙️, sitten Äänet, ja poista käytöstä \"Hiljainen tila\"."
        ]
      }
    },
    toast: {
      added: "Lisätty",
      removed: "Poistettu"
    },
    feedback: {
      prompt: "Miten Buddy toimii sinulle?",
      easy: "Helppo 👍",
      hard: "Vaikea 👎",
      thanks: "Kiitos palautteesta!",
      easyThanks: "Hienoa kuulla!",
      hardSorry: "Pahoittelut. Mikä oli vaikeaa?",
      placeholder: "Mikä oli epäselvää? (valinnainen)",
      send: "Lähetä",
      skip: "Ohita",
      sent: "✓ Kiitos!",
      shareTitle: "Tunnethan jonkun, joka pitäisi Buddystä?",
      shareBody: "Käytän Buddya — yksinkertainen sovellus vanhemmille perheenjäsenille. Yhden painalluksen soitot, lääkemuistutukset, huijaustunnistus. Ilmainen, ei rekisteröitymistä.",
      shareButton: "Jaa Buddy"
    }
  }
};

// Expose for app.js
if (typeof window !== 'undefined') window.TRANSLATIONS = TRANSLATIONS;