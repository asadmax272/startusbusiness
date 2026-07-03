import Link from "next/link";

const NAV = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/orders", label: "Orders" },
  { href: "/dashboard/llc-status", label: "LLC Status" },
  { href: "/dashboard/ein-status", label: "EIN Status" },
  { href: "/dashboard/documents", label: "Documents" },
  { href: "/dashboard/support", label: "Support" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex">
      <aside className="w-56 border-r border-line bg-ink-raised p-6 hidden md:block">
        <Link href="/" className="font-display font-700 text-paper block mb-8">
          StartUSBusiness
        </Link>
        <nav className="space-y-1">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="block text-sm text-mist hover:text-paper hover:bg-line rounded-sm px-3 py-2 transition-colors"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-6 md:p-10 max-w-4xl">{children}</main>
    </div>
  );
}
