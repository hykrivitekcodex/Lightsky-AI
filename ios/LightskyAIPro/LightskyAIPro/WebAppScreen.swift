import SwiftUI

struct WebAppScreen: View {
    @State private var isLoading = true
    @State private var errorMessage: String?
    @State private var reloadID = UUID()

    var body: some View {
        NavigationStack {
            ZStack {
                LightskyWebView(
                    url: AppConfig.webAppURL,
                    isLoading: $isLoading,
                    errorMessage: $errorMessage,
                    reloadID: $reloadID
                )
                .ignoresSafeArea(.container, edges: .bottom)

                if isLoading {
                    VStack(spacing: 12) {
                        LogoMark(size: 72)
                        Text("Loading Lightsky AI")
                            .font(.headline.weight(.700))
                            .foregroundStyle(.secondary)
                    }
                    .padding(22)
                    .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
                }

                if let errorMessage {
                    errorView(message: errorMessage)
                }
            }
            .navigationTitle(AppConfig.appName)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        reloadID = UUID()
                    } label: {
                        Image(systemName: "arrow.clockwise")
                    }
                    .accessibilityLabel("Reload Lightsky AI")
                }
            }
        }
    }

    private func errorView(message: String) -> some View {
        VStack(spacing: 14) {
            LogoMark(size: 62)
            Text("Lightsky could not connect")
                .font(.headline.weight(.800))
            Text(message)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
            Button {
                reloadID = UUID()
            } label: {
                Label("Try again", systemImage: "arrow.clockwise")
                    .font(.headline.weight(.700))
            }
            .buttonStyle(.borderedProminent)
        }
        .padding(22)
        .frame(maxWidth: 360)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
        .padding()
    }
}

#Preview {
    WebAppScreen()
}
