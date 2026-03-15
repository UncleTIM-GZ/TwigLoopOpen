"use client";

import { useState } from "react";

interface ApplyForm {
  orgName: string;
  contactName: string;
  email: string;
  phone: string;
  region: string;
  problemToSolve: string;
  targetAudience: string;
  desiredHelp: string;
  existingResources: string;
  repoLink: string;
  additionalNotes: string;
  fileLink: string;
}

const INITIAL_FORM: ApplyForm = {
  orgName: "",
  contactName: "",
  email: "",
  phone: "",
  region: "",
  problemToSolve: "",
  targetAudience: "",
  desiredHelp: "",
  existingResources: "",
  repoLink: "",
  additionalNotes: "",
  fileLink: "",
};

export default function PublicBenefitApplyPage() {
  const [form, setForm] = useState<ApplyForm>(INITIAL_FORM);
  const [submitted, setSubmitted] = useState(false);

  function update<K extends keyof ApplyForm>(key: K, value: ApplyForm[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center justify-center gap-4 py-20">
        <div className="h-12 w-12 rounded-full bg-green-400/20 flex items-center justify-center">
          <span className="text-green-400 text-xl">✓</span>
        </div>
        <h2 className="font-mono text-xl font-bold text-green-400">
          Request Submitted
        </h2>
        <p className="text-gray-400 text-sm text-center max-w-md">
          Your request has been recorded. During Public Beta, all applications
          are processed via email within 3-5 business days. For urgent requests,
          please email:{" "}
          <a
            href="mailto:beta@twigloop.dev"
            className="text-green-400 hover:underline"
          >
            beta@twigloop.dev
          </a>
        </p>
        <button
          onClick={() => {
            setForm(INITIAL_FORM);
            setSubmitted(false);
          }}
          className="mt-4 rounded-md border border-gray-700 px-4 py-2 text-sm text-gray-300 hover:border-green-400 hover:text-green-400 transition-colors"
        >
          Submit Another Request
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className="font-mono text-2xl font-bold text-green-400 mb-2">
        Public Benefit Request
      </h1>

      {/* Explanation banner */}
      <div className="mb-8 rounded-md border border-green-400/30 bg-green-400/5 px-4 py-3">
        <p className="text-sm text-green-300">
          Testing phase — all applications are reviewed manually via email. We
          will reach out once your request is processed.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-8">
        {/* Section: Organization Info */}
        <Section title="Organization Information">
          <Field label="Organization Name" required>
            <input
              type="text"
              value={form.orgName}
              onChange={(e) => update("orgName", e.target.value)}
              required
              placeholder="e.g. Hope Foundation"
              className={inputClass}
            />
          </Field>
          <Field label="Contact Name">
            <input
              type="text"
              value={form.contactName}
              onChange={(e) => update("contactName", e.target.value)}
              placeholder="Primary contact person"
              className={inputClass}
            />
          </Field>
          <Field label="Email" required>
            <input
              type="email"
              value={form.email}
              onChange={(e) => update("email", e.target.value)}
              required
              placeholder="contact@example.org"
              className={inputClass}
            />
          </Field>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Phone">
              <input
                type="tel"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
                placeholder="+86 ..."
                className={inputClass}
              />
            </Field>
            <Field label="Region">
              <input
                type="text"
                value={form.region}
                onChange={(e) => update("region", e.target.value)}
                placeholder="e.g. Beijing, China"
                className={inputClass}
              />
            </Field>
          </div>
        </Section>

        {/* Section: Request Description */}
        <Section title="Request Description">
          <Field label="Problem to Solve" required>
            <textarea
              value={form.problemToSolve}
              onChange={(e) => update("problemToSolve", e.target.value)}
              required
              rows={3}
              placeholder="Describe the core problem your organization faces..."
              className={inputClass}
            />
          </Field>
          <Field label="Target Audience">
            <input
              type="text"
              value={form.targetAudience}
              onChange={(e) => update("targetAudience", e.target.value)}
              placeholder="Who will benefit from this project?"
              className={inputClass}
            />
          </Field>
          <Field label="Desired Help" required>
            <textarea
              value={form.desiredHelp}
              onChange={(e) => update("desiredHelp", e.target.value)}
              required
              rows={3}
              placeholder="What kind of technical help do you need?"
              className={inputClass}
            />
          </Field>
          <Field label="Existing Resources">
            <textarea
              value={form.existingResources}
              onChange={(e) => update("existingResources", e.target.value)}
              rows={2}
              placeholder="Any existing tools, systems, or team members already involved..."
              className={inputClass}
            />
          </Field>
          <Field label="Repository / Technical Materials Link">
            <input
              type="url"
              value={form.repoLink}
              onChange={(e) => update("repoLink", e.target.value)}
              placeholder="https://github.com/..."
              className={inputClass}
            />
          </Field>
        </Section>

        {/* Section: Additional Notes */}
        <Section title="Additional Notes">
          <Field label="Notes">
            <textarea
              value={form.additionalNotes}
              onChange={(e) => update("additionalNotes", e.target.value)}
              rows={3}
              placeholder="Anything else we should know..."
              className={inputClass}
            />
          </Field>
          <Field label="File Link">
            <input
              type="url"
              value={form.fileLink}
              onChange={(e) => update("fileLink", e.target.value)}
              placeholder="Link to supporting documents (Google Drive, etc.)"
              className={inputClass}
            />
          </Field>
        </Section>

        <button
          type="submit"
          className="self-start rounded-md bg-green-400 px-6 py-2.5 text-sm font-medium text-gray-950 hover:bg-green-300 transition-colors"
        >
          Submit Request
        </button>
      </form>
    </div>
  );
}

/* ---- Shared sub-components ---- */

const inputClass =
  "w-full rounded-md border border-gray-700 bg-gray-900 px-3 py-2 text-sm text-gray-200 placeholder:text-gray-600 focus:border-green-400 focus:outline-none focus:ring-1 focus:ring-green-400/40 transition-colors";

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <fieldset className="flex flex-col gap-4">
      <legend className="font-mono text-sm font-semibold text-gray-400 uppercase tracking-wider mb-1">
        {title}
      </legend>
      {children}
    </fieldset>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-sm text-gray-400">
        {label}
        {required && <span className="text-green-400 ml-1">*</span>}
      </span>
      {children}
    </label>
  );
}
