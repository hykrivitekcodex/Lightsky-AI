import SwiftUI

struct SettingsScreen: View {
    var body: some View {
        NavigationStack {
            List {
                Section {
                    HStack(spacing: 14) {
                        LogoMark(size: 52)
                        VStack(alignment: .leading, spacing: 2) {
                            Text(AppConfig.appName)
                                .font(.headline.weight(.800))
                            Text(AppConfig.byline)
                                .foregroundStyle(.secondary)
                        }
                    }
                    .padding(.vertical, 6)
                }

                Section("App") {
                    LabeledContent("Version", value: "1.0")
                    LabeledContent("Platform", value: "iOS")
                    LabeledContent("Hosted app", value: AppConfig.webAppURL.host ?? "Lightsky")
                }

                Section("Links") {
                    Link("Open release page", destination: AppConfig.releaseURL)
                    Link("Email Krivi", destination: URL(string: "mailto:\(AppConfig.labsEmail)")!)
                }
            }
            .navigationTitle("Settings")
        }
    }
}

#Preview {
    SettingsScreen()
}
