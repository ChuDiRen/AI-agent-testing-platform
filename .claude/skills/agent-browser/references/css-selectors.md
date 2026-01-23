# CSS Selectors and Locators Reference

## Common CSS Selectors

### Basic Selectors
- `element` - Element type selector (e.g., `button`, `input`, `div`)
- `.class` - Class selector (e.g., `.btn-primary`, `.form-control`)
- `#id` - ID selector (e.g., `#submit-btn`, `#login-form`)
- `*` - Universal selector (all elements)

### Attribute Selectors
- `[attribute]` - Has attribute (e.g., `[disabled]`)
- `[attribute=value]` - Exact match (e.g., `[type="text"]`)
- `[attribute^=value]` - Starts with (e.g., `[class^="btn-"]`)
- `[attribute$=value]` - Ends with (e.g., `[class$="-primary"]`)
- `[attribute*=value]` - Contains (e.g., `[class*="form"]`)

### Combinators
- `selector1 selector2` - Descendant (e.g., `form input`)
- `selector1 > selector2` - Direct child (e.g., `ul > li`)
- `selector1 + selector2` - Adjacent sibling
- `selector1 ~ selector2` - General sibling

### Pseudo-classes
- `:hover` - Mouse over element
- `:focus` - Element has focus
- `:active` - Element being clicked
- `:disabled` - Disabled element
- `:checked` - Checked checkbox/radio
- `:first-child` - First child
- `:last-child` - Last child
- `:nth-child(n)` - Nth child
- `:not(selector)` - Negation

## Form-Specific Selectors

### Input Types
- `input[type="text"]` - Text input
- `input[type="password"]` - Password input
- `input[type="email"]` - Email input
- `input[type="submit"]` - Submit button
- `input[type="checkbox"]` - Checkbox
- `input[type="radio"]` - Radio button
- `textarea` - Text area
- `select` - Dropdown select

### Form Patterns
- `form input` - All inputs in forms
- `form button[type="submit"]` - Submit buttons
- `.form-group input` - Inputs in form groups
- `.error-message` - Error messages
- `.validation-error` - Validation errors

## Navigation and Layout

### Navigation Elements
- `nav a` - Navigation links
- `.navbar` - Navigation bar
- `.menu` - Menu elements
- `.breadcrumb` - Breadcrumb navigation

### Content Areas
- `main` - Main content area
- `article` - Article content
- `section` - Content sections
- `.container` - Container divs
- `.row` - Grid rows
- `.col-*` - Grid columns

## Interactive Elements

### Buttons and Actions
- `button` - Button elements
- `.btn` - Styled buttons
- `.btn-primary` - Primary buttons
- `.btn-secondary` - Secondary buttons
- `[role="button"]` - Elements acting as buttons

### Links and Clickable Elements
- `a` - Links
- `a[href]` - Links with href
- `.link` - Styled links
- `[onclick]` - Elements with click handlers

## Common Patterns for Web Testing

### Login Forms
```css
#username, #email, #user
#password, #pass
#login, #signin, .btn-login
```

### Search Forms
```css
#search, #q, .search-input
.search-btn, .btn-search
```

### Tables
```css
table.data-table
tbody tr
thead th
td:nth-child(n)
```

### Lists and Cards
```css
.item-list > li
.card, .tile
.grid-item
```

## Best Practices

1. **Use stable selectors**: Prefer classes and IDs over element types
2. **Avoid brittle selectors**: Don't rely on auto-generated classes
3. **Be specific but not too specific**: Balance specificity with maintainability
4. **Use semantic selectors**: Prefer meaningful class names
5. **Test selectors**: Verify selectors work across different page states

## Troubleshooting

### Common Issues
- **Dynamic classes**: Use data attributes or stable parent elements
- **Shadow DOM**: Use custom element selectors
- **iframes**: Switch to iframe context first
- **Timing issues**: Use wait commands before selecting

### Debugging Tips
- Use browser dev tools to test selectors
- Check for multiple matches when expecting one
- Verify element visibility and interactability
- Consider page load timing and dynamic content
