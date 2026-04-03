import "./globals.css";
import Link from "next/link";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main>
          <h1>RR Control Panel</h1>
          <nav style={{ display: "flex", gap: 12, marginBottom: 20 }}>
            <Link href="/dashboard">Dashboard</Link>
            <Link href="/accounts">Accounts</Link>
            <Link href="/tags">Tags</Link>
            <Link href="/calculators">Calculators</Link>
            <Link href="/logs">Logs</Link>
            <Link href="/settings">Settings</Link>
          </nav>
          {children}
        </main>
      </body>
    </html>
  );
}
