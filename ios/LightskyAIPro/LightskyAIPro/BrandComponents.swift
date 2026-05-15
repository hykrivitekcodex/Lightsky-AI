import SwiftUI

struct BrandHeader: View {
    var trailingText: String? = nil

    var body: some View {
        HStack(spacing: 14) {
            LogoMark(size: 54)

            VStack(alignment: .leading, spacing: 2) {
                Text(AppConfig.appName)
                    .font(.title2.weight(.800))
                    .foregroundStyle(.primary)

                Text(AppConfig.byline)
                    .font(.subheadline.weight(.600))
                    .foregroundStyle(.secondary)
            }

            Spacer()

            if let trailingText {
                Text(trailingText)
                    .font(.subheadline.weight(.700))
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
        }
        .padding(18)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 28, style: .continuous))
        .overlay(alignment: .bottom) {
            Capsule()
                .fill(siriGradient)
                .frame(height: 2)
                .padding(.horizontal, 20)
        }
    }
}

struct LogoMark: View {
    var size: CGFloat

    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: size * 0.32, style: .continuous)
                .fill(siriGradient)
                .shadow(color: .blue.opacity(0.16), radius: 16, x: 0, y: 10)

            Text(AppConfig.logo)
                .font(.system(size: size * 0.48, weight: .bold))
        }
        .frame(width: size, height: size)
        .accessibilityLabel("Lightsky AI logo")
    }
}

struct SoftPanel<Content: View>: View {
    @ViewBuilder var content: Content

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            content
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay(alignment: .top) {
            Capsule()
                .fill(siriGradient)
                .frame(height: 2)
                .padding(.horizontal, 18)
        }
    }
}

let siriGradient = LinearGradient(
    colors: [.cyan, .blue, .purple, .pink, .orange, .yellow, .green],
    startPoint: .leading,
    endPoint: .trailing
)
