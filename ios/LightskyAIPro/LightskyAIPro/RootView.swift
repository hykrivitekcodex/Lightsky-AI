import SwiftUI

struct RootView: View {
    @State private var selectedTab: AppTab = .chat

    var body: some View {
        TabView(selection: $selectedTab) {
            WebAppScreen()
                .tabItem {
                    Label(AppTab.chat.title, systemImage: AppTab.chat.systemImage)
                }
                .tag(AppTab.chat)

            LabsScreen()
                .tabItem {
                    Label(AppTab.labs.title, systemImage: AppTab.labs.systemImage)
                }
                .tag(AppTab.labs)

            DownloadsScreen()
                .tabItem {
                    Label(AppTab.downloads.title, systemImage: AppTab.downloads.systemImage)
                }
                .tag(AppTab.downloads)

            SettingsScreen()
                .tabItem {
                    Label(AppTab.settings.title, systemImage: AppTab.settings.systemImage)
                }
                .tag(AppTab.settings)
        }
        .tint(.pink)
    }
}

#Preview {
    RootView()
}
