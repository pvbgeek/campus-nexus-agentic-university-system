# Campus Nexus UI packet — version 1

Prepared for Kavya Sharma's CSEN 296 UI design contribution. Team: Parth Bhalerao, Calianna Collins, Dana Steinke, Noelle Evanich, Kavya Sharma.

## Open the prototype

Extract the ZIP. Open `index.html` in a browser. All fonts, CSS, JavaScript, and product PNGs are local; no build, login, API key, or network is needed. Start at Store → My orders → Request a refund → My cases. Staff workspace and Reports are separate design demonstrations. The complete source is editable.

## Deliverables

- Six primary page designs: storefront, orders, refund request, case tracking, staff case review, reports/oversight.
- Eight desktop PNG exports including the component/style reference and eight-state reference sheet.
- Six mobile PNG exports at 390 px width; desktop exports are 1440 px wide.
- Four original transparent-background product PNGs: hoodie, tote, mug, notebook.
- Catalog JSON with sample SKUs, prices, alt text, and relative image paths.
- Shared CSS, HTML page sources, lightweight prototype JavaScript, and an illustrated PDF packet.

PNG page exports are static visual mockups rendered from the HTML. Form controls in the exports are drawn as static controls for reliable rendering. The editable HTML keeps actual form elements. Minor differences are possible between static exports and browser rendering.

## Visual direction

SCU-inspired cardinal, warm paper/stone neutrals, serif editorial headings, restrained gold accents. This is a fictional UCS identity, not an official SCU identity. No official seal or campus logo is used.

| Token | Value | Usage |
|---|---|---|
| Cardinal | #802238 | Primary buttons, wordmark, highlights |
| Ink | #262522 | Primary text |
| Muted ink | #68635E | Supporting text |
| Warm paper | #FAF8F4 | Page canvas |
| Soft stone | #F0EDE7 | Product backgrounds, quiet panels |
| Antique gold | #B08D57 | Decorative accent, notice rule |
| Success ink | #285C3B | Processed/verified states |
| Focus | #006D77 | Keyboard focus outline |

Typography: Georgia headings, Arial body/controls. Base body 15 px; heading 49 px desktop / 39 px mobile hero. 8 px spacing rhythm, light borders, restrained corner radius. Gold is decorative, not low-contrast body text.

## Page map and backend handoff

| Page | HTML | Required server data/action |
|---|---|---|
| Store | store.html / index.html | Read product catalog. Purchasing/cart/checkout is outside this packet. |
| Orders | orders.html | Retrieve only the authenticated customer's orders/items and refundable balances. |
| Refund | refund.html | Create a case from order/item, decimal amount, reason, and description; assign server-generated case ID. |
| Cases | cases.html | Read authorized case status/timeline; receive case message and mock email notifications. |
| Staff review | staff.html | Read assigned queue; record reasoned supervisor decision; check authorization at execution. |
| Reports | reports.html | Shared weekly ledger, decision outcomes/reasons, audit records, supervisor revocation. |
| UI states | states.html | Reference copy for approved, denied, pending review, weekly limit, validation, revocation, empty, and unavailable states. |
| Design system | design-system.html | Shared visual tokens/components. |

Backend names/routes should follow the team's implementation. These HTML filenames are prototype routes, not required API endpoint names.

## Interaction scope and limits

Implemented locally in prototype code: linked navigation, form input validation (positive amount, up to two decimals, at most $64 for the selected sample item), request confirmation display, required decision reason, confirm dialogs, toast feedback, and a visual authority-revoked message.

All actions are simulated and nonpersistent. The staff view is accessible by a prototype link for review; it is not role-protected. Revocation changes a display message only; it does not revoke a live agent. Nothing sends email, authenticates a user, issues money, calls an LLM, retrieves RAG records, or enforces server authority. Sample values reset when pages reload; screens do not share a live state store. The case-tracking screen is a fixed under-review sample. The confirmation page is a separate local interaction state.

Queue filters and storefront products are presentational. Support/policy/accessibility footer labels are design placeholders. Dedicated policy administration/upload, mock inbox management, login, product detail, and audit-detail pages remain future UI scope. Do not report these as implemented.

## State and security rules for integration

- Treat submitted content as untrusted; render it as text, not raw HTML.
- Resolve customer identity server-side. A customer ID supplied in a form is not access authority.
- Scope records and tools to the assigned case. Never disclose unrelated customers through search, errors, or reports.
- Required authority limits: $100 per autonomous transaction; shared $500 per UTC week starting Monday 00:00. Use integer cents and a transactional ledger.
- Recheck permissions, cumulative total, supervisor decisions, and revocation at execution, not only when the page loads.
- A $125 request is escalated, not silently reduced to $100. Staff approval does not bypass configured autonomous limits.
- Refund destination comes from the authorized profile; the request does not accept bank redirection.
- Keep submitted, approved, and successfully processed statuses distinct. Confirmation of submission must never say payment was issued.
- Use idempotency and disable duplicate submissions while a request is pending. A retry must not create another refund.
- Logs should capture case/decision IDs, actor, policy version, timestamp, authorization result, and actual execution result without full banking data.

## Proposed store policy — team review needed

For mockup content only: requests within 30 days of delivery for a damaged item, incorrect item, or verified duplicate charge; the amount cannot exceed the remaining refundable balance. For a duplicate charge, verify that the duplicate was actually posted and anchor the window to the charge date. Final eligibility wording, evidence requirements, return treatment, exclusions, and exceptions need team agreement and must match the implemented policy. The 30-day rule is a design proposal, not a professor-supplied requirement.

## Sample data consistency

Customer Avery Chen (CUST-001), order NX-2048: hoodie $64 + journal $12 = $76. Sample refund case NX-1042 requests $64 for the hoodie. Already processed weekly amounts $100 + $95 + $100 + $80 = $375. If NX-1042 executes, the total becomes $439; $61 remains. NX-1043 is a separate $125 escalation. Pending request total is $189. A denied $24 case does not count toward processed totals.

Sample week shown: November 9–15, 2026, UTC. This is fixed demonstration data.

## Accessibility and responsive acceptance checklist

The source includes semantic headings, explicit field labels, alt text, text-based status labels, keyboard focus outlines, and a live region for feedback. Desktop layouts use columns; mobile stacks panels, retains customer navigation, and puts wide staff ledgers inside a horizontal scroll container. Staff pages remain directly accessible from filenames/demo footer on mobile.

Before app integration is accepted: test keyboard-only operation, screen reader announcements/focus after errors and confirmation, all enabled/disabled controls, 200% zoom, 320/390/768/1440 px layouts, actual text/background contrast, and real authorization failures. Replace native confirm dialogs with accessible in-app dialogs if the final app requires a custom component system. Set focus to errors or confirmation headings and preserve entered data after failures.

## Validation performed

PNG images and PDF pages were rendered and visually reviewed; asset loading, local HTML references, product dimensions/transparency, and JavaScript syntax were checked. Browser automation could not launch in this environment, so interactions have not received an end-to-end browser pass. That remains a required integration check; static mockups do not establish a functional or secure backend.

## Suggested progress-report contribution wording

Kavya prepared the Campus Nexus UI design packet for the fictional University Campus Store. The deliverable includes six primary page designs, desktop and mobile visual exports, a shared design system, eight reference UI states, and four AI-generated transparent product PNG assets. An editable HTML/CSS/JavaScript prototype illustrates the customer refund journey and staff review/oversight screens. The packet documents proposed policy text, sample data, accessibility considerations, and backend integration requirements. Live agent integration and server-side controls remain team implementation work.

## Product assets and generation provenance

Generated using the built-in image-generation tool. All four use a shared prompt: one isolated ecommerce catalog PNG for fictional UCS; premium realistic studio product photography; soft even light; centered full object with safe margins; truly transparent background; subtle contact shadow; no unrelated objects, pricing, watermark, or official university seal.

- `assets/hoodie.png`: cardinal heavyweight collegiate pullover hoodie, cream embroidered uppercase UCS, hood and kangaroo pocket, front-facing with no person.
- `assets/tote.png`: natural ivory canvas book tote, cardinal handles, cardinal UCS wordmark, standing three-quarter view.
- `assets/mug.png`: ivory ceramic mug, cardinal interior/handle, UCS letters, three-quarter view.
- `assets/notebook.png`: cardinal cloth-bound hardcover notebook, cream UCS letters and thin gold rule, closed three-quarter view.

The catalog prices are invented test values, not real SCU product prices. Keep the supplied PNGs unmodified in the asset folder and use `object-fit: contain` to preserve proportions.
