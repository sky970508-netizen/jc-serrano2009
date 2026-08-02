import Foundation
import PDFKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let doc = PDFDocument(url: url) else { exit(1) }
for p in 0..<doc.pageCount {
    guard let page = doc.page(at: p) else { continue }
    let n = page.numberOfCharacters
    var start = 0
    var lastY = Double.nan
    var minX = Double.infinity, maxX = -Double.infinity
    func flush(_ end: Int) {
        guard end > start else { return }
        let sel = page.selection(for: NSRange(location: start, length: end - start))
        let s = (sel?.string ?? "").replacingOccurrences(of: "\n", with: " ")
            .trimmingCharacters(in: .whitespaces)
        if !s.isEmpty {
            print(String(format: "%d\t%.1f\t%.1f\t%.1f\t%@", p+1, lastY, minX, maxX, s))
        }
    }
    for i in 0..<n {
        let r = page.characterBounds(at: i)
        if r.width <= 0 && r.height <= 0 { continue }
        let y = Double(r.midY)
        if lastY.isNaN || abs(lastY - y) < 3.5 {
            if lastY.isNaN { lastY = y; start = i }
            minX = min(minX, Double(r.minX)); maxX = max(maxX, Double(r.maxX))
        } else {
            flush(i)
            start = i; lastY = y; minX = Double(r.minX); maxX = Double(r.maxX)
        }
    }
    flush(n)
}
