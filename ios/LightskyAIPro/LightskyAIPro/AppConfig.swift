import Foundation

enum AppConfig {
    static let appName = "Lightsky AI pro"
    static let byline = "by Krivi"
    static let logo = "✨"
    static let webAppURL = URL(string: "https://lightsky-ai-krivi.streamlit.app/?startup=done")!
    static let labsURL = URL(string: "https://lightsky-ai-krivi.streamlit.app/labs")!
    static let releaseURL = URL(string: "https://github.com/hykrivitekcodex/Lightsky-AI/releases/tag/v3.0")!
    static let desktopEXEURL = URL(string: "https://github.com/hykrivitekcodex/Lightsky-AI/releases/download/v3.0/LightskyAIPro.exe")!
    static let setupEXEURL = URL(string: "https://github.com/hykrivitekcodex/Lightsky-AI/releases/download/v3.0/LightskyAIProSetup.exe")!
    static let labsEmail = "krivi.ezhil@gmail.com"
}

enum AppTab: String, CaseIterable, Identifiable {
    case chat
    case labs
    case downloads
    case settings

    var id: String { rawValue }

    var title: String {
        switch self {
        case .chat:
            return "Chat"
        case .labs:
            return "Labs"
        case .downloads:
            return "Downloads"
        case .settings:
            return "Settings"
        }
    }

    var systemImage: String {
        switch self {
        case .chat:
            return "sparkles"
        case .labs:
            return "flask"
        case .downloads:
            return "arrow.down.circle"
        case .settings:
            return "gearshape"
        }
    }
}
