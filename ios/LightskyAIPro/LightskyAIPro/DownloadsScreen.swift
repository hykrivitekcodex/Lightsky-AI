import SwiftUI

struct DownloadsScreen: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    BrandHeader(trailingText: "v3.0")

                    SoftPanel {
                        Text("Desktop App")
                            .font(.title2.weight(.800))
                        Text("Download the Windows build from the official Lightsky AI release.")
                            .foregroundStyle(.secondary)
                    }

                    Link(destination: AppConfig.desktopEXEURL) {
                        Label("Download desktop app", systemImage: "arrow.down.circle.fill")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)

                    Link(destination: AppConfig.setupEXEURL) {
                        Label("Download setup installer", systemImage: "shippingbox")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)

                    Link(destination: AppConfig.releaseURL) {
                        Label("Open release page", systemImage: "link")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Downloads")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

#Preview {
    DownloadsScreen()
}
