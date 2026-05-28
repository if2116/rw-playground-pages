# Team Content

This directory maintains team member data for the About page.

## Files

- `members.zh.json`: Chinese team member content.
- `members.en.json`: English team member content.

## Rules

- Keep `id`, `order`, and `image` consistent between Chinese and English files.
- Sort members by `order` ascending.
- Store long biographies as paragraph arrays in `bio`.
- Store images under `public/team`.
- Do not maintain team member biographies in `Content/About`; About keeps page-level content only.
