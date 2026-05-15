import SwiftUI

struct LabsScreen: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    BrandHeader(trailingText: "Labs")

                    SoftPanel {
                        Text("Lightsky Labs")
                            .font(.title2.weight(.800))
                        Text("to join labs and collaborate with krivi send out an email to \(AppConfig.labsEmail)")
                            .font(.body)
                            .foregroundStyle(.secondary)
                    }

                    Link(destination: mailURL) {
                        Label("Email Krivi", systemImage: "envelope")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)

                    Link(destination: AppConfig.labsURL) {
                        Label("Open Labs", systemImage: "safari")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Labs")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    private var mailURL: URL {
        URL(string: "mailto:\(AppConfig.labsEmail)")!
    }
}

#Preview {
    LabsScreen()
}
