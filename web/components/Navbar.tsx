import Link from "next/link";

const links = [
  { href: "/apartments", label: "Apartments" },
  { href: "/amenities", label: "Amenities" },
  { href: "/optimality", label: "Optimality" },
];

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-slate-200 sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="font-semibold text-brand-600 text-lg">
          Optipoint
        </Link>
        <div className="flex gap-1">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="px-3 py-1.5 rounded-md text-sm font-medium text-slate-700 hover:bg-brand-50 hover:text-brand-600 transition"
            >
              {l.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
