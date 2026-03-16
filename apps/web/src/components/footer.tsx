import Link from "next/link";

const FOOTER_LINKS = [
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
  { href: "/cookies", label: "Cookies" },
  { href: "/security-policy", label: "Security" },
  { href: "/privacy-requests", label: "Privacy Requests" },
  { href: "/beta-notice", label: "Beta Notice" },
];

export function Footer() {
  return (
    <footer className="border-t border-gray-800/50 px-6 py-6 mt-12">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <p className="font-mono text-xs text-gray-600">
          &copy; 2026 Twig Loop &middot; Operated by Timothy Ou
        </p>
        <div className="flex flex-wrap items-center gap-4">
          {FOOTER_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="font-mono text-xs text-gray-600 hover:text-gray-400 transition-colors"
            >
              {link.label}
            </Link>
          ))}
          <a
            href="mailto:hello@twigloop.tech"
            className="font-mono text-xs text-gray-600 hover:text-green-400 transition-colors"
          >
            Contact
          </a>
        </div>
      </div>
    </footer>
  );
}
