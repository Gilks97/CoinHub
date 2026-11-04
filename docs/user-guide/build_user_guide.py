"""
Build the CoinHub User Guide PDF.

Usage:   pip install reportlab
         python docs/user-guide/build_user_guide.py
Output:  docs/user-guide/CoinHub-User-Guide.pdf  (next to this script)

Edit the CONTACT DETAILS and VERSION values below, then re-run.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, NextPageTemplate,
)

# ============================ EDIT THESE ====================================
VERSION = "1.0"
UPDATED = "November 2026"

# CONTACT DETAILS: fill in before sharing the PDF
TECH_NAME = "[Gilks97]"
TECH_PHONE = "[Phone / WhatsApp number]"
TECH_EMAIL = "[moseti97@gmail.com]"
TECH_HOURS = "[Support hours, e.g. Mon-Fri 8am-6pm]"
WEBSITE = "https://coinhub-kjam.onrender.com"
# ============================================================================

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CoinHub-User-Guide.pdf")

NAVY = colors.HexColor("#1e2430")
GOLD = colors.HexColor("#c9a84c")
GOLD_LIGHT = colors.HexColor("#f7f0dc")
GREY = colors.HexColor("#4a5568")
LIGHT = colors.HexColor("#edf2f7")
RED_LIGHT = colors.HexColor("#fdecea")
RED = colors.HexColor("#c0392b")
GREEN_LIGHT = colors.HexColor("#e8f6ee")
GREEN = colors.HexColor("#1e8449")

W, H = A4
LM = RM = 20 * mm
TM = 22 * mm
BM = 20 * mm
CW = W - LM - RM

# ----------------------------- styles --------------------------------------
base = ParagraphStyle("base", fontName="Helvetica", fontSize=10.5, leading=15, textColor=colors.HexColor("#1a202c"))
body = ParagraphStyle("body", parent=base, spaceAfter=6)
small = ParagraphStyle("small", parent=base, fontSize=9, leading=12.5, textColor=GREY)
h_part = ParagraphStyle("h_part", parent=base, fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=NAVY, spaceAfter=4)
h_part_sub = ParagraphStyle("h_part_sub", parent=base, fontSize=11, textColor=GREY, spaceAfter=10)
h1 = ParagraphStyle("h1", parent=base, fontName="Helvetica-Bold", fontSize=14.5, leading=18, textColor=NAVY, spaceBefore=12, spaceAfter=5)
h2 = ParagraphStyle("h2", parent=base, fontName="Helvetica-Bold", fontSize=11.5, leading=15, textColor=NAVY, spaceBefore=6, spaceAfter=3)
cell = ParagraphStyle("cell", parent=base, fontSize=9.5, leading=13)
cell_b = ParagraphStyle("cell_b", parent=cell, fontName="Helvetica-Bold")
cell_h = ParagraphStyle("cell_h", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
bullet = ParagraphStyle("bullet", parent=base, leftIndent=14, bulletIndent=3, spaceAfter=2.5)
cover_title = ParagraphStyle("ct", parent=base, fontName="Helvetica-Bold", fontSize=36, leading=42, textColor=colors.white)
cover_sub = ParagraphStyle("cs", parent=base, fontSize=14, leading=20, textColor=colors.HexColor("#e2e8f0"))
cover_small = ParagraphStyle("csm", parent=base, fontSize=10.5, leading=15, textColor=GOLD)


def P(text, style=body):
    return Paragraph(text, style)


def bullets(items):
    return [Paragraph(t, bullet, bulletText="-") for t in items]


def tbl(rows, widths, header=True, zebra=True):
    data = []
    for i, r in enumerate(rows):
        st = cell_h if (header and i == 0) else cell
        data.append([c if not isinstance(c, str) else Paragraph(c, st) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e0")),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    if zebra:
        for i in range(1 if header else 0, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    return t


def box(title, lines, bg=GOLD_LIGHT, edge=GOLD, title_color=NAVY):
    inner = [Paragraph("<b>%s</b>" % title, ParagraphStyle("bt", parent=base, textColor=title_color, spaceAfter=3))]
    for ln in lines:
        if isinstance(ln, str):
            inner.append(Paragraph(ln, ParagraphStyle("bl", parent=base, fontSize=10, leading=14, spaceAfter=2)))
        else:
            inner.append(ln)
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def steps(items):
    rows = []
    for i, (title, text) in enumerate(items, 1):
        num = Paragraph("<b>%d</b>" % i, ParagraphStyle("n", parent=base, fontSize=13, textColor=colors.white, alignment=TA_CENTER))
        content = [Paragraph("<b>%s</b>" % title, ParagraphStyle("st", parent=base, spaceAfter=1.5)),
                   Paragraph(text, ParagraphStyle("sx", parent=base, fontSize=10, leading=14, textColor=GREY))]
        rows.append([num, content])
    t = Table(rows, colWidths=[11 * mm, CW - 11 * mm])
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
             ("LEFTPADDING", (1, 0), (1, -1), 9),
             ("LINEBELOW", (0, 0), (-1, -2), 0.4, colors.HexColor("#e2e8f0"))]
    for i in range(len(rows)):
        style.append(("BACKGROUND", (0, i), (0, i), NAVY))
    t.setStyle(TableStyle(style))
    return t


# ------------------------- page decorations --------------------------------
def cover_page(c, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.rect(0, H - 14 * mm, W, 14 * mm, stroke=0, fill=1)
    c.rect(LM, 40 * mm, 40 * mm, 1.2 * mm, stroke=0, fill=1)
    c.restoreState()


def normal_page(c, doc):
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(LM, H - 14 * mm, W - RM, H - 14 * mm)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(NAVY)
    c.drawString(LM, H - 11.5 * mm, "CoinHub User Guide")
    c.setFont("Helvetica", 9)
    c.setFillColor(GREY)
    c.drawRightString(W - RM, H - 11.5 * mm, "Version %s  |  %s" % (VERSION, UPDATED))
    c.setStrokeColor(colors.HexColor("#cbd5e0"))
    c.setLineWidth(0.5)
    c.line(LM, 14 * mm, W - RM, 14 * mm)
    c.drawString(LM, 9 * mm, "Need help? Contact the technician (see the last page).")
    c.drawRightString(W - RM, 9 * mm, "Page %d" % doc.page)
    c.restoreState()


# ------------------------------ content ------------------------------------
story = []

# Cover
story += [Spacer(1, 70 * mm),
          P("CoinHub", cover_title),
          Spacer(1, 4 * mm),
          P("User Guide", ParagraphStyle("c2", parent=cover_title, fontSize=26, leading=32, textColor=GOLD)),
          Spacer(1, 8 * mm),
          P("Buying coins with M-Pesa, and handling orders in the admin panel", cover_sub),
          Spacer(1, 62 * mm),
          P("Part 1: For customers<br/>Part 2: For staff", cover_sub),
          Spacer(1, 6 * mm),
          P("Version %s  |  %s" % (VERSION, UPDATED), cover_small),
          NextPageTemplate("normal"), PageBreak()]

# About / contents
story += [
    P("About this guide", h_part),
    P("This guide explains how to use CoinHub in plain language. It shows what to do at each step, what the messages mean, and when a problem is too complicated to fix yourself and you should contact the technician.", body),
    Spacer(1, 3 * mm),
    tbl([
        ["Part", "Who it is for", "What it covers"],
        ["<b>Part 1</b>", "Customers", "Buying coins, how prices work, what the screens mean, fixing simple problems"],
        ["<b>Part 2</b>", "Staff", "Signing in to the admin panel, handling paid orders, copying User IDs, prices and coins"],
        ["<b>Last page</b>", "Everyone", "How to reach the technician and what to have ready"],
    ], [24 * mm, 32 * mm, CW - 56 * mm]),
    Spacer(1, 6 * mm),
    box("The golden rule", [
        "If something looks wrong with <b>money</b> (you were charged but it failed, you were charged twice, or the numbers do not match), <b>do not try again and do not pay twice.</b> Keep your evidence and contact the technician."
    ], bg=RED_LIGHT, edge=RED, title_color=RED),
    Spacer(1, 6 * mm),
    P("Words used in this guide", h1),
    tbl([
        ["Word", "Meaning"],
        ["<b>App User ID</b>", "The number that identifies your account inside the app you are buying coins for (1 to 10 digits)."],
        ["<b>STK Push / M-Pesa prompt</b>", "The pop-up that appears on your phone asking you to enter your M-Pesa PIN to approve the payment."],
        ["<b>Reference</b>", "The order number CoinHub gives you, for example CH2410260001. Keep it."],
        ["<b>M-Pesa receipt</b>", "The code in your M-Pesa confirmation SMS, for example RGQ12345XY."],
        ["<b>Loaded</b>", "Our team has put the coins into your account in the app."],
        ["<b>Technician</b>", "The person who looks after the CoinHub system and fixes technical problems."],
    ], [48 * mm, CW - 48 * mm]),
    PageBreak(),
]

# ------------------------------ PART 1 -------------------------------------
story += [
    P("Part 1: For customers", h_part),
    P("How to buy coins safely and easily", h_part_sub),

    P("1. What CoinHub does", h1),
    P("CoinHub lets you top up coins for supported apps and pay with M-Pesa. You do not need to create an account. You choose the app, enter your details, approve the payment on your phone, and our team loads the coins into your app account.", body),
    box("Good to know", [
        "Payment is instant, but <b>loading coins is done by our team</b>, so the coins do not arrive in the same second you pay.",
    ]),

    P("2. Before you start", h1),
    P("Have these ready:", body),
]
story += bullets([
    "<b>Your App User ID</b>: the number shown in your account or profile inside the app. It must be digits only, up to 10 digits.",
    "<b>Your M-Pesa number</b> with enough balance, and your phone switched on with network signal.",
    "<b>How many coins you want.</b> The minimum is <b>1,000 coins</b>, and you can only buy in steps of 1,000 (1,000, 2,000, 3,000 and so on).",
])
story += [
    Spacer(1, 2 * mm),
    P("You can type your phone number in any of these ways. They are all accepted:", body),
    tbl([
        ["Style", "Example"],
        ["Starting with 7", "7XX XXX XXX  (for example 712 345 678)"],
        ["Starting with 07", "07XX XXX XXX  (for example 0712 345 678)"],
        ["Starting with 01", "01XX XXX XXX  (for example 0112 345 678)"],
    ], [50 * mm, CW - 50 * mm]),
    Spacer(1, 2 * mm),
    box("Check your User ID carefully", [
        "Coins are loaded to the User ID you enter. A wrong ID can send your coins to someone else, and this cannot always be corrected."
    ], bg=RED_LIGHT, edge=RED, title_color=RED),
    PageBreak(),

    P("3. Step by step: buying coins", h1),
    steps([
        ("Choose your app",
         "Open the CoinHub website. Tap the app you want to buy coins for. (The <b>All Apps</b> link at the top takes you back to the list.)"),
        ("Enter your details",
         "Type your <b>App User ID</b>, your <b>M-Pesa Number</b> and the <b>Coins to Purchase</b>. The <b>Amount Payable</b> in KES updates as you type. When everything is correct the <b>Continue to Confirm</b> button turns on. If it stays grey, one of the fields is not valid yet (see the table on the next page)."),
        ("Check the summary",
         "The Order Summary shows the app, your User ID, your M-Pesa number, the coins and the total. Read each line. If something is wrong, press <b>Back</b> and fix it."),
        ("Pay via M-Pesa",
         "Press <b>Pay via M-Pesa</b>. A prompt appears on your phone. Enter your M-Pesa PIN <b>on that prompt only</b> to approve."),
        ("Wait for confirmation",
         "The screen says <b>Processing Payment</b> and counts up (for example 3/20). It checks every few seconds for about one minute. This is not a countdown of your money; it is CoinHub checking whether M-Pesa has confirmed. Do not close the page."),
        ("See the result",
         "<b>Payment Received!</b> means success. Write down or screenshot the <b>Reference</b> and the <b>M-Pesa Receipt</b>. Our team will now load your coins."),
    ]),
    Spacer(1, 4 * mm),
    P("When the Continue button will not turn on", h2),
    tbl([
        ["Field", "What is needed"],
        ["App User ID", "Digits only, 1 to 10 digits. Letters or spaces are not allowed."],
        ["M-Pesa Number", "A valid Kenyan number in one of the styles shown above."],
        ["Coins to Purchase", "At least 1,000 and a multiple of 1,000. A red warning appears if the number is not valid (for example 1,500)."],
    ], [38 * mm, CW - 38 * mm]),
    PageBreak(),

    P("4. How prices work", h1),
    P("Each app has a price for <b>every 1,000 coins</b>. Your total is that price multiplied by the number of thousands you buy. M-Pesa can only charge <b>whole shillings</b>, so if the exact total has cents, it is rounded <b>up</b> to the next shilling.", body),
    tbl([
        ["Example price per 1,000 coins", "You buy 1,000", "You buy 5,000"],
        ["KES 15", "KES 15", "KES 75"],
        ["KES 15.4", "KES 16 (15.4 rounded up)", "KES 77"],
        ["KES 1.6", "KES 2 (1.6 rounded up)", "KES 8"],
    ], [66 * mm, 52 * mm, CW - 118 * mm]),
    Spacer(1, 2 * mm),
    P("Prices can change from time to time. <b>The amount shown on the Order Summary is exactly what you will pay.</b>", body),

    P("5. What the screens mean", h1),
    tbl([
        ["You see", "It means", "What to do"],
        ["Processing Payment... Checking (n/20)", "Waiting for M-Pesa to confirm", "Approve the prompt on your phone and wait. Do not refresh or pay again"],
        ["Payment Received!", "Payment succeeded", "Keep the Reference and M-Pesa Receipt. Coins will be loaded by our team"],
        ["Payment Failed", "The payment did not go through (cancelled, wrong PIN, not enough balance, or an error)", "Check your balance, then use <b>Try Again</b>. If you were charged, do not retry; contact the technician"],
        ["Timed-out message after the count reaches 20", "No confirmation arrived in time", "Check your M-Pesa SMS. If money left your account, contact the technician with your Reference. Do not pay again"],
    ], [50 * mm, 55 * mm, CW - 105 * mm]),

    P("6. Fixing common problems yourself", h1),
    tbl([
        ["Problem", "Try this"],
        ["No M-Pesa prompt on my phone", "Check the number you entered, make sure the phone is on with signal, wait one minute, then try again once."],
        ["I cancelled the prompt or entered the wrong PIN", "Press Try Again and start a new payment."],
        ["Not enough M-Pesa balance", "Top up your M-Pesa, then start a new payment."],
        ["The website is slow the first time", "It can take a short while to wake up. Wait and refresh once."],
        ["The apps list does not load", "Press <b>Retry</b>, check your internet, and try again in a minute."],
        ["The page looks old or behaves oddly", "Refresh the page. On a computer press Ctrl+Shift+R."],
    ], [58 * mm, CW - 58 * mm]),
    PageBreak(),

    P("7. Stay safe", h1),
]
story += bullets([
    "<b>Never share your M-Pesa PIN</b> with anyone. CoinHub will never ask for your PIN, by call, SMS, WhatsApp or on the website. You enter it only on the M-Pesa prompt on your own phone.",
    "Only use the official CoinHub website address given to you by the team.",
    "Check the <b>User ID</b> and the <b>amount</b> before you approve the prompt.",
    "Keep your <b>Reference</b> and your <b>M-Pesa SMS</b> until your coins arrive.",
    "Do not pay twice for the same order. If unsure, ask first.",
])
story += [
    Spacer(1, 3 * mm),
    P("8. When to contact the technician", h1),
    P("Most problems are fixed by trying again. Contact the technician when:", body),
]
story += bullets([
    "You were <b>charged but the screen says Payment Failed</b>, or you see a timeout message.",
    "You were <b>charged twice</b> for one order.",
    "You see <b>Payment Received</b> but the coins have not arrived after the time our team told you.",
    "You entered the <b>wrong User ID or phone number</b> and already paid.",
    "The website shows an <b>error message</b> that stays after refreshing and trying again.",
    "The <b>price shown looks wrong</b> or different from what you were told.",
    "Anything about your payment looks suspicious.",
])
story += [
    Spacer(1, 3 * mm),
    box("Have this ready when you contact the technician", [
        "1. The <b>Reference</b> (for example CH2410260001)",
        "2. The <b>M-Pesa receipt code</b> from your SMS",
        "3. The <b>M-Pesa number</b> you paid with",
        "4. The <b>App</b> and your <b>App User ID</b>",
        "5. The <b>date and time</b> of the payment",
        "6. A <b>screenshot</b> of what you saw, if possible",
    ]),
    PageBreak(),
]

# ------------------------------ PART 2 -------------------------------------
story += [
    P("Part 2: For staff", h_part),
    P("Handling orders in the admin panel", h_part_sub),

    P("1. Signing in", h1),
    P("Open the admin address given to you (the CoinHub website address followed by <b>/admin/</b>) and sign in with <b>your own</b> username and password.", body),
]
story += bullets([
    "Everyone has their own account. <b>Never share your login.</b> The system records who shipped each order.",
    "Sign out when you finish, especially on a shared phone or computer.",
    "If you cannot sign in, ask the technician. Do not try other people's accounts.",
])
story += [
    P("2. The dashboard", h1),
    P("The home page shows cards for orders today, paid today, pending today, revenue today and revenue this month, followed by the sections you can use: <b>Orders</b>, <b>Payments</b>, <b>Coin Types</b> and others, depending on your permissions.", body),

    P("3. Handling paid orders (your daily job)", h1),
    steps([
        ("Open Orders and filter by Paid",
         "These customers have paid and are waiting for coins. The status badge is green."),
        ("Read the order",
         "Note the <b>App User ID</b>, the <b>coin type</b> (the app) and the <b>coins requested</b>. On a phone, <b>tap the App User ID</b> to copy it. A small message says <i>Copied</i>."),
        ("Load the coins in the app",
         "Do this in the external app, outside CoinHub, using the copied User ID. Double-check the User ID and the amount of coins."),
        ("Press Ship Coins",
         "Only after the coins are loaded, press the green <b>Ship Coins</b> button on that row. CoinHub records the time and your name, and the status becomes <b>Loaded</b>."),
        ("Many at once",
         "To mark several orders, tick them, choose <b>Mark selected orders as Manually Loaded</b> from the Action list and press Go."),
    ]),
    Spacer(1, 3 * mm),
    box("Important", [
        "<b>Only press Ship Coins after the coins are really loaded.</b> The button updates the record immediately and the customer can see it."
    ], bg=RED_LIGHT, edge=RED, title_color=RED),
    PageBreak(),

    P("Order statuses", h1),
    tbl([
        ["Status", "Colour", "Meaning", "Your action"],
        ["Pending", "Orange", "Customer has not finished paying yet", "Nothing. Wait"],
        ["Paid", "Green", "Money received, coins not loaded yet", "Load the coins, then Ship Coins"],
        ["Loaded", "Blue", "Coins loaded and recorded", "Done"],
        ["Failed", "Red", "Payment did not go through", "No coins to load"],
    ], [24 * mm, 22 * mm, 62 * mm, CW - 108 * mm]),

    P("4. Finding an order or a payment", h1),
    P("Use the search box at the top of the list. You can search by <b>order reference</b>, <b>App User ID</b> or <b>phone number</b>. Use the filters on the side for status, app and date.", body),
    P("The <b>Payments</b> section shows the M-Pesa receipt, the result and its description for each payment. Payments are <b>read-only</b> on purpose; nobody can edit them. If a customer says they paid, search by their reference, phone number or M-Pesa receipt and compare it with their SMS.", body),

    P("5. Using the admin on a phone", h1),
]
story += bullets([
    "Tables are wide. <b>Swipe sideways</b> inside the table to see every column.",
    "<b>Tap an App User ID</b> to copy it. Or press and hold to select it and use your phone's Copy option.",
    "Turn your phone sideways for more room.",
])
story += [
    P("6. Prices and coins (authorised staff only)", h1),
    P("If your account is allowed to, you can change prices and hide coins:", body),
    steps([
        ("Open Coin Types", "Find the app in the list."),
        ("Change the price", "Edit <b>Price per 1000</b> (the KES price for 1,000 coins), then press <b>Save</b>. The customer website uses the new price straight away."),
        ("Hide an app", "To stop selling an app, untick <b>Active</b> and save. It disappears from the website but your history stays safe."),
    ]),
    Spacer(1, 2 * mm),
    P("Prices are rounded up to whole shillings at payment time. Very low prices (under KES 2 per 1,000 coins) still cost at least KES 1.", small),
    PageBreak(),

    P("7. Do and do not", h1),
    tbl([
        ["Do", "Do not"],
        ["Use your own account and sign out when done", "Share your password or let others use your account"],
        ["Load the coins first, then press Ship Coins", "Press Ship Coins before the coins are loaded"],
        ["Check the User ID twice before loading", "Guess or change a User ID"],
        ["Hide an app (untick Active) when it should not be sold", "Delete apps, orders or payments. Only a superadmin can delete, and only when the technician agrees"],
        ["Keep the customer's reference and M-Pesa receipt when escalating", "Promise a refund or a fix before the technician has checked"],
        ["Report anything unusual immediately", "Share customer phone numbers or receipts in public chats or posts"],
    ], [CW / 2, CW / 2]),

    P("8. When to consult the technician", h1),
    P("Handle normal paid orders yourself. Contact the technician when:", body),
]
story += bullets([
    "A customer says they <b>paid but the order is still Pending or shows Failed</b>.",
    "An order's <b>amount or M-Pesa receipt does not match</b> the customer's SMS.",
    "You see <b>duplicate orders</b> or the same payment appearing twice.",
    "An order shows <b>Paid</b> but the <b>User ID looks invalid</b> or the customer reports a wrong ID.",
    "The admin shows an <b>error page</b>, loads very slowly, or looks broken.",
    "You <b>cannot sign in</b>, or you notice activity you did not do.",
    "You need a <b>new app, a new price structure, a new staff account</b> or different permissions.",
    "Anything makes you <b>unsure whether money is involved correctly</b>.",
])
story += [
    Spacer(1, 3 * mm),
    box("Information to give the technician", [
        "Order <b>reference</b>, <b>M-Pesa receipt</b>, customer <b>phone number</b>, <b>App User ID</b>, <b>time</b> of the payment, what you did, and a <b>screenshot</b> of any error. Do not share your password.",
    ]),
    PageBreak(),

    # Contacts
    P("Contact the technician", h_part),
    P("Keep this page where you can find it", h_part_sub),
    Table([
        [Paragraph("<b>Technician</b>", cell_b), Paragraph(TECH_NAME, cell)],
        [Paragraph("<b>Phone / WhatsApp</b>", cell_b), Paragraph(TECH_PHONE, cell)],
        [Paragraph("<b>Email</b>", cell_b), Paragraph(TECH_EMAIL, cell)],
        [Paragraph("<b>Support hours</b>", cell_b), Paragraph(TECH_HOURS, cell)],
        [Paragraph("<b>CoinHub website</b>", cell_b), Paragraph(WEBSITE, cell)],
    ], colWidths=[45 * mm, CW - 45 * mm], style=TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
        ("BACKGROUND", (0, 0), (0, -1), GOLD_LIGHT),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ])),
    Spacer(1, 8 * mm),
    box("Quick reminder", [
        "- Never share your <b>M-Pesa PIN</b> or your <b>admin password</b>.",
        "- Do not pay twice. Contact the technician first.",
        "- Always keep the <b>Reference</b> and the <b>M-Pesa receipt</b>.",
    ]),
    Spacer(1, 8 * mm),
    P("This guide describes CoinHub version %s as of %s. Screens may change over time; ask the technician for the latest version of this guide." % (VERSION, UPDATED), small),
]


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                          title="CoinHub User Guide", author="CoinHub",
                          subject="How to use CoinHub: customers and staff")
    frame_cover = Frame(LM, BM, CW, H - TM - BM, id="cover", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_norm = Frame(LM, BM, CW, H - TM - BM, id="normal", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame_cover], onPage=cover_page),
        PageTemplate(id="normal", frames=[frame_norm], onPage=normal_page),
    ])
    doc.build(story)
    print("Wrote", OUT)


if __name__ == "__main__":
    build()
