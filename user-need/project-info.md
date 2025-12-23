* Project name
You can change this at any time.
ElevenDops

* Elevator pitch
Provide a short tagline for the project. You can change this later.

An AI-powered medical assistant that transforms doctor-patient communication through ElevenLabs voice technology—enabling doctors to create personalized health education audio, deploy intelligent voice agents for patient Q&A, and gain insights into patient concerns before appointments.

An AI voice medical assistant that personalizes education, handles patient Q&A, and reveals concerns ahead of appointments.

* About the project
Be sure to write what inspired you, what you learned, how you built your project, and the challenges you faced. Format your story in Markdown, with LaTeX support for math.

## Inspiration

Healthcare communication may be inefficient. Doctors spend countless hours repeating the same basic medical explanations—pre- and post-operative care, medication instructions, and disease management—to different patients. At the same time, patients struggle to ask or remember everything discussed during short appointments and lack an accessible way to get questions answered at home. We saw an opportunity to bridge this gap with advanced voice AI technology.


## What it does

ElevenDops is an intelligent medical assistant system that revolutionizes doctor-patient communication:

- **Knowledge Upload**: Doctors upload medical education documents that sync to an AI knowledge base
- **Education Audio**: Generate professional TTS audio from medical scripts for patients to listen anytime
- **Agent Setup**: Configure AI voice assistants with customizable personalities (professional, friendly, educational)
- **Patient Conversations**: Patients interact with AI agents via text/voice to get answers to their health questions
- **Conversation Logs**: Doctors review patient questions and concerns before appointments, enabling more focused consultations

## How we built it

We architected ElevenDops with a clean separation of concerns:

- **Frontend**: Streamlit for rapid MVP development with a multi-page application structure
- **Backend**: FastAPI handling all business logic, ElevenLabs API integration, and data management
- **Database**: Firestore as the foundation databse, with ElevenLabs Knowledge Base as a synchronized copy
- **Voice AI**: ElevenLabs APIs for Knowledge Base management, Agent creation, Text-to-Speech, and Conversational AI
- **Infrastructure**: Docker Compose with Firestore Emulator and fake-gcs-server for local development, Cloud Run for production deployment

We followed API-first design principles to ensure future scalability and potential migration to Next.js/TypeScript.

## Challenges we ran into

- **Emulator Configuration**: Setting up local development with Firestore Emulator and fake-gcs-server required careful configuration to match production behavior
- **Real-time Voice Streaming**: Implementing WebSocket-based voice conversations while maintaining conversation state proved complex
- **Medical Compliance**: Ensuring all AI-generated content goes through doctor approval before patient access required careful workflow design
- **Data Synchronization**: Keeping Firestore and ElevenLabs Knowledge Base in sync with proper error handling and retry mechanisms

## Accomplishments that we're proud of

- Built a complete end-to-end medical assistant system from concept to working MVP
- Achieved seamless integration with ElevenLabs' full API suite (Knowledge Base, Agents, TTS, Conversational AI)
- Designed an architecture that requires only configuration changes to move from local development to cloud production
- Implemented property-based testing with Hypothesis for robust code validation

## What we learned

- Deep understanding of ElevenLabs Conversational AI capabilities and best practices
- How to design systems that work identically in local emulator and cloud production environments
- The importance of clear separation between UI and business logic for maintainability
- Medical domain requirements around content approval and patient data handling

## What's next for ElevenDops

- **Voice Input**: Enable real-time voice input for patients using WebSocket streaming
- **Authentication**: Implement secure doctor login and patient session management
- **Webhook Integration**: Automatic conversation analysis via ElevenLabs webhooks
- **Analytics Dashboard**: Advanced insights into patient questions and conversation patterns
- **Multi-language Support**: Expand beyond Traditional Chinese to serve broader patient populations


* Built with
What languages, frameworks, platforms, cloud services, databases, APIs, or other technologies did you use?
`Python` `FastAPI` `Streamlit` `ElevenLabs` `Firestore` `Google Cloud Run` `Google Cloud Storage` `Docker` `Hypothesis` `Pydantic` `Poetry`
 

* What Google Cloud products did you use in this project?
- Cloud Run (containerized application deployment)
- Firestore (NoSQL database for system data)
- Google Cloud Storage (audio file storage)
- Cloud SDK (local development with emulators)

* Please list all other tools or products you used in your project.
- ElevenLabs Conversational AI (voice agents and real-time conversations)
- ElevenLabs Knowledge Base API (medical knowledge management)
- ElevenLabs Text-to-Speech API (education audio generation)
- ElevenLabs Agents API (AI assistant configuration)
- fake-gcs-server (local GCS emulation)
- Firebase Emulator Suite (local Firestore development)
- Docker Compose (local development orchestration)
- Hypothesis (property-based testing framework)
- Poetry (Python dependency management)