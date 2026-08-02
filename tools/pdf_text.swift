import Foundation
import PDFKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let doc = PDFDocument(url: url) else { exit(1) }
for i in 0..<doc.pageCount {
    print("=== PAGE \(i+1) ===")
    print(doc.page(at: i)?.string ?? "")
}
