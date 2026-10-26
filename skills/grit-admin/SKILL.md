---
name: grit-admin
description: >-
  The Grit admin panel: resource definitions, the data table, the form builder,
  dashboard widgets, the sidebar, bulk actions and the system pages. Use for
  "add an admin screen", "the admin table", "a dashboard widget", "the form is
  wrong", "customise the admin", "the sidebar".
---

# grit-admin

The admin generates itself from your models. A resource definition is a
declaration of how a model is presented, and the table, the form, the filters
and the detail view are all derived from it. The work worth doing here is
rarely building a screen: it is making the declaration say the right thing.

```bash
grit docs search "admin"
grit docs show /docs/admin/resources
```

## The resource definition is the screen

`defineResource()` is where columns, form fields, filters and actions are
declared. Change the declaration and every surface follows. Write a custom
page and you have taken on the maintenance of something that used to update
itself.

So the order of preference, strongest first:

1. **Change the declaration.** A column, a filter, a form field, an action.
2. **Change the model.** If the admin shows the wrong thing because the model
   is the wrong shape, fix the model and regenerate. The admin is a symptom
   here, not the problem.
3. **Add a widget or a custom action** for something genuinely outside CRUD.
4. **Write a page by hand**, last, and only when the thing is not a resource
   at all. An Operations page that stitches four queries together is a real
   page. A list of invoices is not.

## The table

Sorting, filtering, selection and pagination are built in. What you decide:

**Which columns.** The default is every field, which is almost always wrong. A
table is a scanning surface: the columns are the ones a person scans for.
Everything else belongs on the detail view. A table with fourteen columns is a
table nobody reads.

**What the label column is.** A relationship renders the related model's own
label column. If a related model has no human label, the dropdown shows ids
and the table shows nothing useful, and the fix is on the related model.

**What the empty state says.** A table with no rows should say what to do, not
"No data".

**Money and dates.** Money is formatted, right-aligned, and grouped with
separators as you type in a form, because `50000000` is unreadable and
`50,000,000` is not. Dates use the project's timezone from the profile, not
the browser's.

## The form

The form builder covers the field types. The parts that go wrong:

**A conditional field belongs in the resource declaration**, not in a
`useEffect` that hides it. The declaration is read by the Go validation, the
Zod schema and the form, so one place stays consistent; a frontend-only
condition means the API still accepts what the form hid.

**Validation comes from the shared Zod schema**, generated from the Go binding
tags. A second hand-written rule in the form is how the form accepts something
the API then rejects with a 422 nobody can explain.

**Every interactive element needs all eight states**, and the two always
missing are error and success. A submit with no loading state double-submits.

**A label must be attached to its control.** Twelve of thirteen form fields
once shipped with a label attached to nothing, which is invisible unless you
test with a keyboard or a screen reader, which is to say invisible to the
people who demonstrate it and not to the people who use it.

## Bulk actions

Bulk create and bulk edit open a grid on a list page. Two things to know:
bulk create validates each row against the model's binding tags, so a bad row
reports itself rather than failing the batch; and a money column written
through a map-shaped update needs the map form, because a struct `Save`
discards what a `BeforeUpdate` hook set.

## Widgets

Stats, charts and activity feeds. A widget earns its place by answering a
question somebody actually asks at the start of the day. "Total contacts" is a
number; "contacts with no activity in 30 days" is a question.

For charts, keep to the project's accent and semantic colours. A chart with
six arbitrary colours is the single clearest tell that a dashboard was
generated rather than designed.

## The sidebar and its icon trap

The sidebar is grouped, collapsible, and uses Lucide icons.

**An icon in the admin's `iconMap` is not automatically a named export from
`@/lib/icons`.** A new page that imports the icon directly fails to build, or
worse renders nothing, until the icon is added to the export block as well as
the map. Two places, every time.

## The system pages

Jobs, Files, Cron, Mail Preview, Trash, Sessions, API Keys and the routes
screen already exist. Before building an operational screen, check whether it
is already there:

```bash
grit docs search "system pages"
grit routes
```

The routes screen has no access column, and that is not an oversight: gin
exposes a route's last handler and nothing in front of it, so the middleware
chain cannot be recovered at runtime. The static table in `internal/access`
is how anything learns which routes are protected, and inventing an access
column from path shapes would be a confident guess presented as fact.

## The design system is already decided

Dark by default, on the tokens in `references/grit-invariants.md`. Onest for
UI, JetBrains Mono for code. The feel is Linear, Vercel dashboard, Raycast.

Do not redesign it. Do not light-mode it. Do not introduce a second accent.
The admin looking like a premium tool is a product decision that was already
made, and a generic-looking admin is a regression even when every pixel is
aligned.

Two palette notes: `apps/web` has **different** tokens from the admin
(`bg-bg-secondary` and `text-accent` rather than `card` and `primary`), so a
component moved between them renders nothing and says nothing. And a style
(`modern`, `glass`) decides which dashboard file is written, while a theme
(`aurora`, `emerald`) decides the CSS variables and can change at runtime with
`THEME=`. They are different mechanisms with different lifetimes.

## New primitives need Base UI, old ones do not

Everything in `components/ui/` is hand-written against the tokens, and that is
right for anything that is a styled element.

It stops being right when a component needs behaviour: a focus trap, roving
focus, listbox semantics, portalled positioning that survives a scroll
container. Those fail silently for keyboard and screen reader users. For a
**new** primitive that needs real interaction behaviour, use
`@base-ui-components/react`, and add the dependency in the same change that
uses it.

Do not rewrite a working primitive to use it. The relationship pickers, the
confirm modal and the dropzone work and are tested, and a rewrite trades known
behaviour for unknown behaviour to satisfy a preference.

## Before you say it works

**Stand the admin up and look at it.** Not a DOM check, not a grep for a class
name: both will confirm something that is visibly broken.

```bash
cd apps/admin && pnpm dev
```

If the change does not appear, the dev server is the first suspect. A process
running since before your edit serves the old bundle. Kill it by port, remove
`.next`, start again.

Then: tab through the screen with the keyboard, submit the form with bad input
and look at the error state, and check it at phone width.
