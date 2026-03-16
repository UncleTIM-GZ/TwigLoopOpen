import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="font-mono text-6xl font-bold text-green-400">404</h1>
      <div className="mt-4 font-mono text-sm text-gray-500">
        <p>$ cd /requested/path</p>
        <p className="text-red-400 mt-1">
          Error: Not Found - the requested page does not exist
        </p>
      </div>
      <div className="mt-8 font-mono text-xs text-gray-600">
        <p>Perhaps you meant one of these:</p>
        <div className="mt-3 space-y-1">
          <p>
            <Link href="/" className="text-cyan-400 hover:text-cyan-300 transition-colors">
              /home
            </Link>
            {" - "}main page
          </p>
          <p>
            <Link href="/projects" className="text-cyan-400 hover:text-cyan-300 transition-colors">
              /projects
            </Link>
            {" - "}browse projects
          </p>
          <p>
            <Link href="/status" className="text-cyan-400 hover:text-cyan-300 transition-colors">
              /status
            </Link>
            {" - "}platform status
          </p>
          <p>
            <Link href="/help" className="text-cyan-400 hover:text-cyan-300 transition-colors">
              /help
            </Link>
            {" - "}help center
          </p>
        </div>
      </div>
      <Link
        href="/"
        className="mt-10 font-mono text-xs px-4 py-2 border border-green-400/40 text-green-400 hover:bg-green-400/10 transition-colors"
      >
        cd /home
      </Link>
    </div>
  );
}
