import Link from "next/link";

const features = [
  {
    href: "/apartments",
    title: "Apartment Finder",
    desc: "Describe your ideal location in plain English. We parse it with spaCy, fetch nearby apartments from OpenStreetMap, and rank them by weighted distance to the amenities you mentioned.",
    cta: "Find apartments",
  },
  {
    href: "/amenities",
    title: "Amenity Finder",
    desc: "Pick a location and an amenity type. Get a distance-sorted list of matches plotted on an interactive map — hospitals, schools, restaurants, and more.",
    cta: "Explore nearby",
  },
  {
    href: "/optimality",
    title: "Optimality Predictor",
    desc: "An sklearn ensemble classifies whether a location is 'Optimal' based on its distances to 16 amenity categories. Trained on Indian universities; 84% test accuracy.",
    cta: "Predict optimality",
  },
];

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="text-center py-10">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
          AI-powered location intelligence
        </h1>
        <p className="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">
          Find optimal places using natural language, OpenStreetMap data, and
          machine learning. Three tools, one API.
        </p>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        {features.map((f) => (
          <Link
            key={f.href}
            href={f.href}
            className="group block rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-brand-500"
          >
            <h2 className="text-xl font-semibold text-slate-900 group-hover:text-brand-600">
              {f.title}
            </h2>
            <p className="mt-3 text-sm text-slate-600 leading-relaxed">{f.desc}</p>
            <span className="mt-4 inline-block text-sm font-medium text-brand-600 group-hover:translate-x-0.5 transition">
              {f.cta} →
            </span>
          </Link>
        ))}
      </section>

      <section className="rounded-xl bg-white border border-slate-200 p-6">
        <h3 className="font-semibold mb-3">How it works</h3>
        <ol className="text-sm text-slate-600 space-y-2 list-decimal list-inside">
          <li>Your query is parsed with spaCy to extract location + amenity preferences.</li>
          <li>Nominatim geocodes the location; Overpass API fetches nearby POIs.</li>
          <li>16 amenity categories are queried in parallel via <code className="bg-slate-100 px-1 rounded">asyncio.gather</code>; results cached in Redis.</li>
          <li>A weighted scoring function or sklearn classifier ranks results.</li>
        </ol>
      </section>
    </div>
  );
}
