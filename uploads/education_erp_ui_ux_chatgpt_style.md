# Education ERP - Đặc tả UI/UX hiện đại theo phong cách ChatGPT

> Trạng thái: Implementation-ready UI specification  
> Nền tảng: Vue 3 + Frappe UI + Tailwind CSS + Lucide Icons  
> Mục tiêu: Tái tạo ngôn ngữ giao diện hiện đại, tối giản và hiệu quả như ảnh tham chiếu; sử dụng thương hiệu IKE thay vì sao chép logo hoặc nhận diện độc quyền của ChatGPT/OpenAI.

---

## 1. Mục tiêu thiết kế

Giao diện phải tạo cảm giác:

- Sạch, nhẹ và yên tĩnh.
- Tập trung vào nội dung và công việc.
- Mật độ thông tin cao nhưng không chật chội.
- Điều hướng nhanh, ít bước và nhất quán.
- Giống một ứng dụng desktop chuyên nghiệp hơn là website marketing.
- Dễ sử dụng liên tục nhiều giờ cho Admin, Giáo viên và Kế toán.

Không thiết kế landing page. Khi đăng nhập, người dùng vào thẳng workspace phù hợp với vai trò.

### 1.1. Nguyên tắc cốt lõi

1. Một màn hình chỉ có một vùng hành động chính.
2. Dùng layout phẳng; không biến mỗi section thành một card nổi.
3. Card chỉ dùng cho item lặp, modal hoặc công cụ có ranh giới thật sự.
4. Dữ liệu danh sách sử dụng table/list; không dùng grid card nếu không cần.
5. Màu thương hiệu chỉ dùng làm accent, không phủ toàn bộ giao diện.
6. Icon dùng Lucide, không tự vẽ SVG nếu đã có icon tương ứng.
7. Hành động nguy hiểm không đặt cạnh hành động chính mà không có khoảng cách.
8. Trạng thái phải có cả chữ và màu; không chỉ dựa vào màu.
9. Tất cả màn hình có loading, empty, error và permission-denied state.
10. Nội dung không được nhảy layout khi loading hoặc hover.

---

## 2. App shell mục tiêu

Desktop sử dụng ba vùng chính:

```text
┌──────────────────┬────────────────────────┬──────────────────────────────────────┐
│ Primary Sidebar  │ Context Pane           │ Main Workspace                       │
│ 240px            │ 320px                  │ flex: 1                              │
│                  │                        │                                      │
│ Điều hướng       │ Danh sách, bộ lọc,     │ Chi tiết, bảng, lịch, form hoặc      │
│ toàn hệ thống    │ nhóm và tìm kiếm       │ nội dung nghiệp vụ chính             │
└──────────────────┴────────────────────────┴──────────────────────────────────────┘
```

### 2.1. Kích thước

| Thành phần | Desktop lớn | Desktop nhỏ | Tablet | Mobile |
|---|---:|---:|---:|---:|
| Primary Sidebar | 240px | 220px | 64px | 0px/drawer |
| Context Pane | 320px | 280px | 300px hoặc drawer | toàn màn hình |
| Workspace Header | 56px | 56px | 56px | 52px |
| Page padding | 24px | 20px | 16px | 12px |
| Content max width | không giới hạn cứng | không giới hạn cứng | 100% | 100% |

Không đặt toàn bộ ứng dụng vào một container max-width ở giữa. ERP cần tận dụng chiều ngang để hiển thị dữ liệu.

### 2.2. Cấu trúc component

```text
AppShell
├── PrimarySidebar
│   ├── BrandButton
│   ├── NewActionButton
│   ├── GlobalNavigation
│   ├── UtilityNavigation
│   └── UserMenu
├── ContextPane
│   ├── ContextHeader
│   ├── ContextSearch
│   ├── ContextFilters
│   └── ContextList
└── MainWorkspace
    ├── WorkspaceHeader
    ├── WorkspaceToolbar
    ├── WorkspaceContent
    └── OptionalInspectorDrawer
```

### 2.3. Quy tắc hiển thị ba vùng

- Trang danh sách/chi tiết: hiển thị đủ ba vùng.
- Dashboard: Primary Sidebar + Main Workspace; ẩn Context Pane.
- Kanban: Primary Sidebar + Main Workspace; Context Pane chuyển thành filter drawer.
- Calendar: Primary Sidebar + Main Workspace; Context Pane chứa lịch nhỏ và bộ lọc.
- Mobile: chỉ hiển thị một vùng mỗi thời điểm.

### 2.4. Kéo thay đổi kích thước panel

Desktop cho phép kéo divider để thay đổi kích thước:

```text
Primary Sidebar  ║  Context Pane  ║  Main Workspace  ║  Inspector/AI
                 ①                ②                  ③
```

| Divider | Điều khiển | Min | Mặc định | Max |
|---|---|---:|---:|---:|
| ① | Primary Sidebar | 200px | 240px | 320px |
| ② | Context Pane | 260px | 320px | 480px |
| ③ | Inspector/AI Drawer | 340px | 420px | 600px |

Quy tắc:

- Vùng kéo trực quan rộng 1px nhưng hit area tối thiểu 8px.
- Hover/focus đổi divider sang brand-500.
- Khi kéo, cursor là `col-resize`.
- Main Workspace luôn còn tối thiểu 560px trên desktop.
- Nếu không đủ chỗ, ưu tiên đóng Inspector, sau đó chuyển Context Pane thành drawer.
- Kích thước được lưu theo người dùng và loại màn hình.
- Double-click divider trả về kích thước mặc định.
- Nút thu gọn Sidebar vẫn hoạt động độc lập với resize.
- Không resize panel trên mobile.
- Không dùng JavaScript cập nhật liên tục gây giật; dùng `requestAnimationFrame`.

Trạng thái lưu:

```json
{
  "primarySidebarWidth": 240,
  "contextPaneWidth": 320,
  "inspectorWidth": 420,
  "primarySidebarCollapsed": false
}
```

Ưu tiên lưu vào user settings phía server. Có thể dùng `localStorage` làm fallback.

### 2.5. Hỗ trợ bàn phím cho divider

Divider dùng semantic separator:

```html
<div
  role="separator"
  aria-orientation="vertical"
  tabindex="0"
  aria-valuemin="260"
  aria-valuemax="480"
  aria-valuenow="320"
/>
```

- `ArrowLeft`/`ArrowRight`: thay đổi 8px.
- `Shift + ArrowLeft/Right`: thay đổi 32px.
- `Home`: về min.
- `End`: về max.
- `Enter`: reset mặc định.
- Focus ring phải nhìn thấy rõ.

---

## 3. Primary Sidebar

Primary Sidebar có nền hơi khác workspace để tạo phân lớp nhẹ, không dùng border đậm.

### 3.1. Nội dung

Thứ tự đề xuất:

1. Logo IKE và nút thu gọn.
2. Hành động nhanh `Tạo mới`.
3. Tìm kiếm toàn cục.
4. Dashboard.
5. Tuyển sinh.
6. Học viên.
7. Đào tạo.
8. Tài chính.
9. Vận hành.
10. Báo cáo.
11. AI Assistant.
12. Settings và tài khoản ở cuối.

### 3.2. Navigation item

```text
┌──────────────────────────────────┐
│ [icon 18]  Học viên         [12] │
└──────────────────────────────────┘
```

| Thuộc tính | Giá trị |
|---|---|
| Cao | 36px |
| Padding ngang | 10px |
| Khoảng icon-label | 10px |
| Border radius | 6px |
| Font | 14px / 20px / 500 |
| Icon | 18px |
| Hover | neutral-100 |
| Active | neutral-200, chữ đậm hơn |
| Focus | outline 2px brand-500 |

Không dùng pill tròn lớn cho toàn bộ menu. Item active là một nền chữ nhật bo nhẹ.

### 3.3. Nhóm menu

- Nhóm không dùng card.
- Label nhóm dùng chữ 11px, font 600, màu muted.
- Khoảng cách trước nhóm 16px.
- Có thể collapse nếu nhóm có hơn bốn mục.
- Khi sidebar thu gọn, chỉ hiển thị icon và tooltip.

### 3.4. Nút tạo mới

Nút `Tạo mới` là command rõ ràng:

- Icon `Plus`.
- Cao 38px.
- Nền trắng hoặc neutral-0.
- Border neutral-200.
- Hover neutral-100.
- Mở menu theo quyền: Lead, Học viên, Lớp, Hóa đơn, Phiếu thu...

---

## 4. Context Pane

Context Pane tương đương vùng danh sách hội thoại trong ảnh tham chiếu. Trong ERP, đây là danh sách bản ghi hoặc navigation cấp hai.

### 4.1. Header

```text
┌────────────────────────────────────┐
│ Học viên                    [•••]  │  56px
├────────────────────────────────────┤
│ [Search........................]   │
│ [Tất cả] [Đang học] [Cảnh báo]     │
├────────────────────────────────────┤
│ Danh sách bản ghi                  │
└────────────────────────────────────┘
```

- Tiêu đề 16px/24px, font 600.
- Menu `MoreHorizontal` cho import/export/settings.
- Search field cao 36px.
- Filter sử dụng segmented control hoặc menu, không dùng nhiều nút pill rời rạc.

### 4.2. List item

Mỗi item cao ổn định 56-72px:

- Dòng 1: tên chính, 14px/20px/500.
- Dòng 2: metadata, 12px/16px, muted.
- Bên phải: thời gian, badge hoặc số tiền.
- Active: neutral-200.
- Hover: neutral-100.
- Không có shadow.
- Không có border từng item; dùng divider khi cần.

Ví dụ học viên:

```text
Nguyễn Văn An                         Cảnh báo
STU-2026-0034 · N5-TP-001             2 buổi vắng
```

### 4.3. Virtualization và pagination

- Danh sách trên 200 item phải có pagination hoặc virtual list.
- Giữ vị trí scroll khi mở rồi quay lại.
- Không tải toàn bộ dữ liệu chỉ để filter tại client.
- Search debounce 250ms.

---

## 5. Main Workspace

Main Workspace là vùng nội dung lớn nhất, nền trắng hoặc gần trắng.

### 5.1. Workspace Header

Header cao 56px, sticky:

```text
┌──────────────────────────────────────────────────────────────────┐
│ [←] Nguyễn Văn An / STU-2026-0034      [Share] [•••] [Save]     │
└──────────────────────────────────────────────────────────────────┘
```

- Bên trái: back button khi cần, title, breadcrumb ngắn.
- Bên phải: command theo trang.
- Không nhồi filter vào header nếu filter thuộc danh sách.
- Primary action nằm ngoài cùng bên phải.
- Header dùng border-bottom 1px neutral-200.

### 5.2. Workspace Content

- Padding mặc định 24px.
- Section cách nhau 32px.
- Section title 15px/22px/600.
- Nội dung form tối đa 760px khi cần đọc theo chiều dọc.
- Table và calendar được phép full width.
- Detail page không bọc toàn bộ nội dung trong card.

### 5.3. Toolbar

Toolbar dùng cho:

- Filter.
- Sort.
- View switcher.
- Bulk action.
- Export.

Quy tắc:

- Cao 40px.
- Icon button 32x32px.
- Dùng tooltip cho icon không rõ nghĩa.
- View mode dùng segmented control.
- Không có hai hàng toolbar trên desktop.

---

## 6. Design tokens

### 6.1. Màu

Giao diện dùng palette trung tính, với đỏ IKE làm accent có kiểm soát.

```css
:root {
  --color-bg-app: #f7f7f8;
  --color-bg-sidebar: #f2f3f5;
  --color-bg-context: #fafafa;
  --color-bg-workspace: #ffffff;
  --color-bg-hover: #ececef;
  --color-bg-active: #e5e5e9;

  --color-border-subtle: #e7e7ea;
  --color-border-default: #d9d9de;
  --color-border-strong: #b8b8c0;

  --color-text-primary: #202123;
  --color-text-secondary: #5f6368;
  --color-text-muted: #8a8f98;
  --color-text-inverse: #ffffff;

  --color-brand-50: #fff1f2;
  --color-brand-100: #ffe0e3;
  --color-brand-500: #d71920;
  --color-brand-600: #b91219;
  --color-brand-700: #941016;

  --color-success-50: #edf8f1;
  --color-success-600: #18794e;
  --color-warning-50: #fff8e6;
  --color-warning-700: #8a5a00;
  --color-danger-50: #fff0f0;
  --color-danger-600: #c43232;
  --color-info-50: #eef5ff;
  --color-info-600: #2864b7;
}
```

Không dùng gradient trong app shell, header, button hoặc card.

### 6.2. Typography

Font:

```css
font-family:
  Inter,
  ui-sans-serif,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

| Token | Size/line-height | Weight | Dùng cho |
|---|---|---:|---|
| display | 28/36 | 650 | Dashboard title đặc biệt |
| h1 | 22/30 | 650 | Page title |
| h2 | 18/26 | 600 | Section lớn |
| h3 | 15/22 | 600 | Panel/section |
| body | 14/21 | 400 | Nội dung chính |
| body-medium | 14/21 | 500 | Label/list title |
| small | 12/18 | 400 | Metadata |
| caption | 11/16 | 500 | Group label, helper |

Quy tắc:

- `letter-spacing: 0`.
- Không scale font theo viewport width.
- Không dùng uppercase cho đoạn text dài.
- Số tiền dùng `font-variant-numeric: tabular-nums`.

### 6.3. Spacing

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
```

Không dùng spacing tùy ý ngoài scale nếu không có lý do rõ ràng.

### 6.4. Radius và shadow

| Component | Radius |
|---|---:|
| Button/input/menu item | 6px |
| Card/item lặp | 8px |
| Modal/drawer | 10px |
| Avatar | 50% |

Shadow:

```css
--shadow-menu: 0 8px 24px rgb(0 0 0 / 0.10);
--shadow-modal: 0 18px 50px rgb(0 0 0 / 0.16);
```

Không dùng shadow cho sidebar, section, table row hoặc form.

### 6.5. Motion

```css
--duration-fast: 120ms;
--duration-normal: 180ms;
--duration-slow: 240ms;
--ease-standard: cubic-bezier(0.2, 0, 0, 1);
```

- Hover: 120ms.
- Drawer/modal: 180-240ms.
- Không animate chiều cao của table lớn.
- Tôn trọng `prefers-reduced-motion`.

---

## 7. Component specification

### 7.1. Button

Variants:

| Variant | Dùng cho |
|---|---|
| Primary | Hành động chính duy nhất của vùng |
| Secondary | Hành động phụ |
| Ghost | Toolbar/header |
| Danger | Delete/cancel nghiêm trọng |
| Icon | Command quen thuộc |

Kích thước:

| Size | Height | Padding | Icon |
|---|---:|---:|---:|
| sm | 30px | 10px | 15px |
| md | 36px | 12px | 17px |
| lg | 40px | 16px | 18px |

Primary button:

- Nền brand-500.
- Hover brand-600.
- Chữ trắng.
- Không gradient.
- Không shadow mặc định.

### 7.2. Icon button

- 32x32px mặc định.
- Icon 17px.
- Radius 6px.
- Tooltip xuất hiện sau 400ms.
- `aria-label` bắt buộc.

### 7.3. Input

- Cao 36px.
- Border 1px neutral.
- Radius 6px.
- Focus ring 2px brand-100, border brand-500.
- Label nằm trên input, không dùng placeholder thay label.
- Error message 12px, danger-600.

### 7.4. Select/menu

- Option set ngắn dùng segmented control.
- Option set dài dùng popover/menu có search.
- Binary dùng switch/checkbox.
- Số lượng dùng input number/stepper.
- Khoảng ngày dùng date range picker.

### 7.5. Badge

Badge cao 22px, radius 5px, chữ 11px/16px/600.

```text
Active      success
Upcoming    info
Warning     warning
Cancelled   neutral
Overdue     danger
```

Không dùng badge cho text không phải trạng thái.

### 7.6. Table

- Header sticky khi bảng dài.
- Row cao 44px hoặc 52px.
- Header 12px/18px/600.
- Không zebra stripe mặc định.
- Hover row neutral-50.
- Selected row brand-50.
- Divider 1px neutral-200.
- Số căn phải.
- Action nằm trong menu `MoreHorizontal`.
- Checkbox chỉ xuất hiện khi hỗ trợ bulk action.

### 7.7. Tabs

- Dùng cho các view cùng một record: Tổng quan, Lớp học, Điểm, Học phí, Lịch sử.
- Tab bar phẳng, border-bottom.
- Active dùng text primary và underline 2px brand.
- Không dùng tab dạng pill nếu có hơn ba tab.

### 7.8. Modal

- Chỉ dùng cho tác vụ ngắn.
- Form dài mở drawer hoặc route riêng.
- Width: 420px, 560px hoặc 720px.
- Header/footer sticky.
- Không đặt card bên trong modal.

### 7.9. Drawer/Inspector

- Width 420px desktop.
- Dùng để xem nhanh hoặc chỉnh sửa nhẹ.
- Không thay thế detail page cho workflow phức tạp.
- Đóng bằng `Esc`, nút X và click backdrop nếu không mất dữ liệu.

### 7.10. Toast

- Góc dưới bên phải desktop.
- Tối đa ba toast.
- Tự đóng sau 4-6 giây với success/info.
- Error quan trọng không tự đóng.
- Không dùng `alert()` trình duyệt.

### 7.11. Command palette

Mở bằng `Ctrl/Cmd + K`.

Hỗ trợ:

- Điều hướng trang.
- Tìm học viên/lớp/giáo viên.
- Tạo mới theo quyền.
- Hành động gần đây.
- Keyboard navigation.

Kết quả phải đến từ backend search có phân quyền.

---

## 8. Page templates

### 8.1. Dashboard

Layout:

```text
Primary Sidebar | Main Workspace

Header: Xin chào + date + quick actions
Row 1: 4 metric tiles phẳng
Row 2: Lịch hôm nay | Cảnh báo cần xử lý
Row 3: Công nợ | Tiến độ lớp | Hoạt động gần đây
```

Metric tile:

- Không shadow.
- Border 1px.
- Radius 8px.
- Cao 96-112px.
- Label 12px.
- Value 26px.
- Trend nhỏ, không dùng biểu đồ trang trí.

### 8.2. Học viên

```text
Primary Sidebar
├── Context Pane: search + filter + student list
└── Main Workspace
    ├── Header: tên, mã, trạng thái, actions
    ├── Tabs
    │   ├── Tổng quan
    │   ├── Đăng ký lớp
    │   ├── Chuyên cần
    │   ├── Điểm số
    │   ├── Học phí
    │   └── Lịch sử
    └── Tab content
```

Tổng quan không dùng ba card lớn. Dùng sections:

- Thông tin cá nhân.
- Người giám hộ.
- Lớp đang học.
- Tiến độ.
- Cảnh báo gần nhất.

### 8.3. Giáo viên

Context Pane:

- Tất cả.
- Đang hoạt động.
- Có lịch hôm nay.
- Chưa phân lớp.

Workspace:

- Hồ sơ.
- Lớp phụ trách.
- Lịch dạy.
- Chuyên môn.
- Hiệu suất/chấm công.

### 8.4. Lớp học

Context Pane là danh sách lớp.

Workspace:

- Header: tên lớp, course, trạng thái.
- Tabs: Tổng quan, Học viên, Lịch học, Nội dung, Điểm danh, Điểm số, Học phí.
- Timeline Session dùng list theo ngày, không dùng card dày đặc.
- `Sinh lịch` là secondary action; `Mở buổi hôm nay` là primary action khi phù hợp.

### 8.5. Điểm danh

Ưu tiên workflow nhanh:

```text
Header: Lớp + ngày + buổi
Toolbar: Có mặt tất cả | Sao chép buổi trước | Lưu
Table:
Học viên | Trạng thái | Đi muộn | Ghi chú
```

- Status dùng segmented control trong mỗi row khi đủ chỗ.
- Mobile dùng select.
- Sticky footer hiển thị tổng số và nút lưu.
- Auto-save draft có indicator, nhưng hoàn tất buổi vẫn cần command rõ ràng.

### 8.6. Nhập điểm

- Chọn loại đánh giá và thông số ở header.
- Table spreadsheet-like.
- Keyboard: Tab/Enter chuyển ô.
- Có paste nhiều dòng từ spreadsheet.
- Hiển thị max score, normalized score và validation ngay tại ô.
- Publish điểm là hành động riêng với lưu draft.

### 8.7. Học phí

Context Pane:

- Tất cả.
- Chưa thu.
- Thu một phần.
- Quá hạn.
- Đã thu.

Workspace:

- Tổng công nợ.
- Invoice list.
- Payment history.
- Timeline chứng từ.
- Nút thu tiền chỉ xuất hiện khi Invoice submitted và còn nợ.

Số tiền luôn:

- Căn phải.
- Tabular numerals.
- Format `4.500.000 ₫`.
- Màu đỏ chỉ dành cho overdue/negative exception.

### 8.8. CRM

Hai view:

- List/table là mặc định.
- Kanban là view tùy chọn.

Kanban:

- Cột full height.
- Card radius 8px.
- Không card lồng card.
- Có số lượng và tổng giá trị ở header cột.
- Drag/drop phải có fallback bằng menu đổi trạng thái.

### 8.9. Calendar

- Month/week/day segmented control.
- Context Pane chứa mini calendar, teacher/class filters.
- Event dùng màu theo loại, không theo từng lớp ngẫu nhiên.
- Click event mở inspector.
- Drag đổi lịch phải kiểm tra conflict trước khi lưu.

### 8.10. Teacher Portal

Mặc định mở `Hôm nay`:

- Lịch dạy hôm nay.
- Session cần hoàn tất.
- Homework cần chấm.
- Học viên cần chú ý.

Không hiển thị menu tài chính hoặc quản trị không liên quan.

### 8.11. Student Portal

Mobile-first:

- Lịch học tiếp theo.
- Tiến độ.
- Homework.
- Điểm mới.
- Nhận xét.
- Công nợ.

Bottom navigation mobile:

- Trang chủ.
- Lịch.
- Bài tập.
- Kết quả.
- Tài khoản.

---

## 9. Responsive behavior

### 9.1. Breakpoints

```css
--breakpoint-mobile: 640px;
--breakpoint-tablet: 1024px;
--breakpoint-desktop: 1280px;
--breakpoint-wide: 1600px;
```

### 9.2. Desktop từ 1280px

- Ba vùng hiển thị đồng thời cho list/detail.
- Sidebar có thể collapse và resize.
- Context Pane resize trong giới hạn được quy định tại mục 2.4.
- Workspace không nhỏ hơn 600px.

### 9.3. Tablet 768-1279px

- Sidebar collapse còn 64px.
- Context Pane có thể cố định 300px.
- Khi Workspace nhỏ hơn 640px, Context Pane chuyển sang drawer.

### 9.4. Mobile dưới 768px

- Primary Sidebar là drawer.
- List và detail là hai route/state riêng.
- Header có back button.
- Table chuyển thành:
  - horizontal scroll nếu cần so sánh; hoặc
  - list row nếu mỗi record độc lập.
- Primary action có thể sticky bottom nhưng không che nội dung.

### 9.5. Không được xảy ra

- Text tràn khỏi button/badge.
- Header action đè page title.
- Modal rộng hơn viewport.
- Table làm toàn trang tràn ngang mà không có vùng scroll riêng.
- Sidebar/context pane khiến workspace dưới 560px trên desktop.

---

## 10. Interaction states

### 10.1. Loading

- Dùng skeleton đúng kích thước nội dung.
- Không dùng spinner toàn màn hình cho list/detail.
- Button đang submit giữ nguyên width và hiển thị spinner nhỏ.
- Không cho submit hai lần.

### 10.2. Empty

Empty state gồm:

- Icon Lucide 32px.
- Tiêu đề ngắn.
- Một câu giải thích.
- Một primary action nếu người dùng có quyền.

Không dùng minh họa lớn hoặc đoạn hướng dẫn dài.

### 10.3. Error

- Inline error cho lỗi field.
- Banner cho lỗi tải section.
- Full-page error chỉ khi route không thể hiển thị.
- Có `Thử lại` khi request có thể retry an toàn.

### 10.4. Permission denied

- HTTP 403 từ backend.
- UI hiển thị icon Lock, thông báo ngắn và nút quay lại.
- Không render dữ liệu rồi mới ẩn.

### 10.5. Unsaved changes

- Dirty state hiển thị ở header.
- Chuyển route hỏi xác nhận.
- Save shortcut `Ctrl/Cmd + S`.
- Auto-save chỉ dùng cho draft phù hợp, không tự submit chứng từ.

---

## 11. Navigation architecture

```text
Dashboard
Tuyển sinh
  Leads
  CRM Pipeline
  Lịch tư vấn
Học viên
  Danh sách
  Onboarding
  Thẻ học viên
Đào tạo
  Chương trình
  Lớp học
  Lịch học
  Điểm danh
  Điểm số
  Homework
  Giáo viên
Tài chính
  Lịch thu
  Hóa đơn
  Phiếu thu
  Hoàn tiền
Vận hành
  Phòng học
  Công việc
Báo cáo
  Đào tạo
  Chuyên cần
  Công nợ
Settings
```

### Quy tắc route

- Route phản ánh record đang mở.
- Refresh không mất context.
- Deep link hoạt động.
- Back/forward của trình duyệt hoạt động đúng.
- Filter quan trọng được lưu trong query string.

Ví dụ:

```text
/education_app/students
/education_app/students/STU-2026-0034
/education_app/classes/CLS-2026-0001/sessions
/education_app/finance/invoices?status=overdue
```

---

## 12. Vue component architecture

```text
frontend/src/
├── app/
│   ├── AppShell.vue
│   ├── PrimarySidebar.vue
│   ├── ContextPane.vue
│   ├── WorkspaceHeader.vue
│   └── route-meta.js
├── components/
│   ├── ui/
│   │   ├── AppButton.vue
│   │   ├── IconButton.vue
│   │   ├── AppInput.vue
│   │   ├── StatusBadge.vue
│   │   ├── SegmentedControl.vue
│   │   ├── DataTable.vue
│   │   ├── EmptyState.vue
│   │   ├── ErrorState.vue
│   │   ├── Skeleton.vue
│   │   ├── AppModal.vue
│   │   └── InspectorDrawer.vue
│   ├── command/
│   │   └── CommandPalette.vue
│   └── domain/
│       ├── StudentListItem.vue
│       ├── ClassListItem.vue
│       ├── AttendanceGrid.vue
│       └── MoneyAmount.vue
├── composables/
│   ├── useListQuery.js
│   ├── usePermissions.js
│   ├── useUnsavedChanges.js
│   └── useResponsivePane.js
├── stores/
│   ├── auth.js
│   ├── ui.js
│   └── recent.js
├── pages/
└── styles/
    ├── tokens.css
    ├── base.css
    └── utilities.css
```

### 12.1. Route metadata

Mỗi route khai báo:

```js
{
  path: "/students/:studentId?",
  component: StudentsPage,
  meta: {
    title: "Học viên",
    icon: "users",
    layout: "list-detail",
    requiredRole: ["Education Admin", "Academic Manager"],
    contextPane: "student-list",
  },
}
```

### 12.2. Không được làm

- Không để từng page tự dựng sidebar/header riêng.
- Không copy button/input style vào từng file.
- Không gọi API trực tiếp lặp lại mà không có composable/resource chuẩn.
- Không hardcode user `Administrator`.
- Không dùng mock data trong production page.
- Không dùng emoji làm icon nghiệp vụ.

---

## 13. CSS implementation baseline

```css
html,
body,
#app {
  width: 100%;
  height: 100%;
  margin: 0;
  overflow: hidden;
}

body {
  background: var(--color-bg-app);
  color: var(--color-text-primary);
  font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 14px;
  line-height: 1.5;
  letter-spacing: 0;
}

.app-shell {
  display: grid;
  grid-template-columns:
    var(--primary-sidebar-width, 240px)
    var(--context-pane-width, 320px)
    minmax(0, 1fr);
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

.primary-sidebar,
.context-pane,
.main-workspace {
  min-width: 0;
  min-height: 0;
}

.primary-sidebar {
  background: var(--color-bg-sidebar);
  border-right: 1px solid var(--color-border-subtle);
}

.context-pane {
  background: var(--color-bg-context);
  border-right: 1px solid var(--color-border-subtle);
}

.main-workspace {
  background: var(--color-bg-workspace);
  overflow: hidden;
}

.workspace-scroll {
  height: calc(100vh - 56px);
  overflow: auto;
  overscroll-behavior: contain;
}
```

---

## 14. Accessibility

Mức mục tiêu: WCAG 2.1 AA cho workflow chính.

Checklist:

- Tất cả button có accessible name.
- Icon-only button có tooltip và `aria-label`.
- Focus nhìn thấy rõ.
- Tab order đúng.
- Modal trap focus.
- `Esc` đóng modal/drawer.
- Table có header semantic.
- Form error liên kết bằng `aria-describedby`.
- Không dùng màu là tín hiệu duy nhất.
- Touch target tối thiểu 40x40px trên mobile.

---

## 15. Dark mode

Không bắt buộc trong giai đoạn đầu.

Kiến trúc CSS phải dùng semantic token để có thể bổ sung sau. Không hardcode màu trực tiếp trong Vue component ngoài trường hợp biểu đồ có bảng màu được định nghĩa tập trung.

---

## 16. AI Assistant

AI Assistant là panel phụ, không che workflow chính.

Desktop:

- Mở bằng icon ở sidebar hoặc `Ctrl/Cmd + .`.
- Hiển thị drawer bên phải rộng 420px.
- Có context của record đang mở nếu người dùng cho phép.

Mobile:

- Mở route/panel toàn màn hình.

Quy tắc:

- Không hardcode API key.
- Gọi backend proxy.
- Hiển thị rõ dữ liệu nào được gửi cho AI.
- Không tự động thực hiện thay đổi dữ liệu.
- Mọi đề xuất ghi dữ liệu phải cho người dùng xác nhận.

---

## 17. Visual QA

Phải kiểm tra ít nhất các viewport:

| Viewport | Mục tiêu |
|---|---|
| 1920x1080 | Ba vùng cân đối, workspace rộng |
| 1440x900 | Layout desktop chuẩn |
| 1280x800 | Không bóp workspace |
| 1024x768 | Sidebar collapse, context responsive |
| 768x1024 | Tablet |
| 390x844 | Mobile |

### 17.1. Screenshot checklist

- Không có overlap.
- Không có text bị cắt sai.
- Không có horizontal page scroll ngoài table cần thiết.
- Header/footer sticky không che nội dung.
- Menu/popover nằm trong viewport.
- Empty/loading/error state đúng kích thước.
- Sidebar active state đúng route.
- Context list giữ scroll.

### 17.2. Playwright verification

Sau mỗi thay đổi lớn:

1. Mở route chính.
2. Chụp screenshot desktop/mobile.
3. Kiểm tra console error.
4. Kiểm tra request lỗi.
5. Tab qua các control chính.
6. Test sidebar collapse.
7. Test list → detail → back.
8. Test modal/drawer và `Esc`.
9. Kéo từng divider đến min/max và chụp screenshot.
10. Reload trang và xác nhận kích thước panel được giữ lại.
11. Test resize bằng bàn phím.

---

## 18. Acceptance criteria

### UI shell

- App shell giống bố cục ba vùng trong ảnh tham chiếu.
- Sidebar, Context Pane và Workspace có scroll độc lập đúng chỗ.
- Không có section dạng floating card bao quanh toàn trang.
- Mọi route dùng chung shell và token.

### Visual

- Nền trung tính, border nhẹ, không gradient.
- Radius không vượt 8px cho card/item thông thường.
- Không dùng emoji thay icon.
- Không có bảng màu một sắc đỏ; đỏ chỉ là accent.
- Typography và spacing đúng token.

### Interaction

- `Ctrl/Cmd + K` mở command palette.
- Sidebar collapse được và nhớ trạng thái.
- Sidebar, Context Pane và Inspector kéo thay đổi kích thước được trên desktop.
- Double-click divider reset kích thước mặc định.
- Reload trang vẫn giữ kích thước đã chọn.
- List/detail hoạt động với browser back/forward.
- Loading không làm nhảy layout.
- Primary action không xuất hiện nhiều hơn một lần trong cùng vùng.

### Responsive

- Desktop hiển thị ba vùng khi phù hợp.
- Tablet không làm Workspace nhỏ hơn mức sử dụng được.
- Mobile dùng drawer/route thay vì ép ba cột.
- Không có overlap tại sáu viewport QA.

### Accessibility

- Keyboard dùng được cho navigation, modal và form.
- Focus visible.
- Contrast đạt AA.
- Icon button có accessible name.

---

## 19. Implementation roadmap

### PR 1 - Design foundation

- Tạo `tokens.css`.
- Chuẩn hóa font, màu, spacing, radius.
- Tạo Button, IconButton, Input, Badge, Tooltip.
- Loại bỏ gradient và style trùng lặp.

### PR 2 - App shell

- Tạo Primary Sidebar.
- Tạo Context Pane.
- Tạo Workspace Header.
- Tạo accessible resize divider cho các panel.
- Lưu và khôi phục kích thước panel.
- Route metadata.
- Responsive pane state.

### PR 3 - Shared data components

- DataTable.
- ContextList.
- Empty/Error/Skeleton.
- Modal/Drawer.
- Command Palette.

### PR 4 - Students list/detail

- Chuyển Students sang template chuẩn.
- Loại bỏ mock/inline style.
- Tabs và permission states.
- Desktop/mobile QA.

### PR 5 - Classes and training

- Classes detail.
- Sessions.
- Attendance.
- Assessments.

### PR 6 - Finance

- Invoice list/detail.
- Payment workflow.
- Money formatting.
- Submitted/cancelled states.

### PR 7 - CRM and operations

- Lead list.
- Optional Kanban.
- Appointments/calendar.
- Task board.

### PR 8 - Role portals

- Teacher Portal.
- Student Portal.
- Role-specific navigation.

### PR 9 - QA and cleanup

- Visual regression screenshots.
- Accessibility.
- Performance.
- Remove dead CSS/components/mock data.

Mỗi PR phải:

- Không thay đổi nghiệp vụ ngoài phạm vi.
- Có screenshot desktop/mobile.
- Chạy build và test.
- Không để console error.
- Cập nhật checklist acceptance liên quan.

---

## 20. Definition of Done cho giao diện

Một màn hình chỉ hoàn thành khi:

1. Dùng AppShell và shared component.
2. Không còn style trùng lặp đáng kể.
3. Không có mock data.
4. Có loading, empty, error, permission state.
5. Responsive ở sáu viewport chuẩn.
6. Keyboard và focus hoạt động.
7. Không có overlap hoặc text overflow.
8. Không có console error.
9. Request thất bại được xử lý.
10. Screenshot được review.
11. Build/test chạy xanh.
12. Product owner nghiệm thu theo acceptance criteria của trang.
13. Divider resize đạt min/max, persistence và keyboard accessibility.

---

## 21. Chỉ dẫn giao cho coding agent

Prompt triển khai nên yêu cầu:

```text
Đọc toàn bộ education_erp_ui_ux_chatgpt_style.md.
Triển khai đúng theo từng PR trong mục Implementation roadmap.
Không làm toàn bộ trong một lượt.
Trước mỗi PR, kiểm tra code hiện tại và liệt kê file sẽ thay đổi.
Sau mỗi PR:
- chạy build/test;
- mở app bằng browser;
- chụp desktop/mobile;
- kiểm tra overlap, overflow, console và network;
- chỉ chuyển PR tiếp theo khi acceptance criteria đã đạt.
Không thay đổi quy tắc nghiệp vụ nếu tài liệu không yêu cầu.
Không dùng mock data, hardcode secret hoặc ignore permission.
```

Coding agent không được tự diễn giải “phong cách ChatGPT” thành:

- Giao diện chat cho mọi chức năng.
- Sidebar màu tối.
- Gradient tím/xanh.
- Card nổi dày đặc.
- Hero marketing.
- Bubble tròn quá mức.

Ý nghĩa chính xác là:

> App shell tối giản, phân vùng rõ, typography sạch, neutral palette, interaction tinh gọn, command palette mạnh và mật độ thông tin phù hợp ứng dụng desktop.
