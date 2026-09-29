package com.oathbound.client.screen;

import com.oathbound.quest.QuestLog;
import com.oathbound.quest.QuestLog.Boon;
import com.oathbound.quest.QuestLog.Quest;
import com.oathbound.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.Style;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Supplier;

/**
 * The Lantern Chronicle: an open, leather-bound book with five silk ribbons.
 * <ul>
 *   <li><b>Chronicle</b>: the story, one chapter unsealing as you reach it.</li>
 *   <li><b>The Path</b>: each chapter's quests drawn as a branching path of seals, with objectives and hints.</li>
 *   <li><b>Tithes &amp; Boons</b>: what the Order owes you (paid at any kindled Wayshrine) and the Oath Boons
 *       you may swear when a chapter closes.</li>
 *   <li><b>Bestiary</b> and <b>Armory</b>: field notes on every creature and relic, unlocked with the story.</li>
 * </ul>
 * The state comes from the Chronicle item's custom data, which the server keeps up to date.
 */
public class ChronicleScreen extends Screen {
    public static final int TAB_STORY = 0, TAB_PATH = 1, TAB_TITHES = 2, TAB_BESTIARY = 3, TAB_ARMORY = 4;
    private static final String[] TAB_KEYS = {"story", "path", "tithes", "bestiary", "armory"};
    private static final int[] TAB_COLORS = {0xFF8C2A2A, 0xFF2F5A8C, 0xFFB08A2E, 0xFF3F6E3A, 0xFF5E3A7A};
    private static final String[] NUMERALS = {"I", "II", "III", "IV", "V", "VI", "VII"};
    private static final int W = 384, H = 236, PAGE_W = 172, PAGE_H = 212;

    // palette
    private static final int LEATHER = 0xFF4A2A18, LEATHER_DARK = 0xFF2A170C, LEATHER_EDGE = 0xFF1A0E07;
    private static final int GOLD = 0xFFD9B35A, GOLD_DIM = 0xFF8C6A2A, GOLD_BRIGHT = 0xFFFFE7A3;
    private static final int PAPER = 0xFFF3E6C6, PAPER_SHADE = 0xFFE3CFA3, PAPER_EDGE = 0xFFB89968;
    private static final int INK = 0xFF2E1F12, INK_SOFT = 0xFF6E5638, INK_FAINT = 0xFFA89070, RUBRIC = 0xFF8C2A2A;
    private static final int C_DONE = 0xFF3E7A3A, C_ACTIVE = 0xFFC9941E, C_LOCKED = 0xFF9A8B72, C_OWED = 0xFFB0532A;

    // ------------------------------------------------------------------ bestiary & armory entries
    private record Entry(String id, int chapter, Supplier<? extends Item> icon) {}

    private static final List<Entry> BEASTS = List.of(
        new Entry("lanternmoth", 0, ModItems.LANTERNMOTH_SPAWN_EGG), new Entry("gloamling", 0, ModItems.GLOAMLING_SPAWN_EGG),
        new Entry("sir_caldris", 1, ModItems.SIR_CALDRIS_SPAWN_EGG), new Entry("animated_tome", 2, ModItems.ANIMATED_TOME_SPAWN_EGG),
        new Entry("archmage_veyl", 2, ModItems.ARCHMAGE_VEYL_SPAWN_EGG), new Entry("barrow_wight", 3, ModItems.BARROW_WIGHT_SPAWN_EGG),
        new Entry("spectral_housecarl", 3, ModItems.SPECTRAL_HOUSECARL_SPAWN_EGG), new Entry("hrodgar", 3, ModItems.HRODGAR_SPAWN_EGG),
        new Entry("forsworn_knight", 4, ModItems.FORSWORN_KNIGHT_SPAWN_EGG), new Entry("veilhound", 5, ModItems.VEILHOUND_SPAWN_EGG),
        new Entry("morvane", 5, ModItems.MORVANE_SPAWN_EGG));

    private static final List<Entry> RELICS = List.of(
        new Entry("wardens_lantern", 0, ModItems.WARDENS_LANTERN), new Entry("oathsteel_longsword", 0, ModItems.OATHSTEEL_LONGSWORD),
        new Entry("wardens_halberd", 0, ModItems.WARDENS_HALBERD), new Entry("lumen_flask", 0, ModItems.LUMEN_FLASK),
        new Entry("drowned_anchor", 1, ModItems.DROWNED_ANCHOR), new Entry("staff_of_veyl", 2, ModItems.STAFF_OF_VEYL),
        new Entry("dawnstring_longbow", 2, ModItems.DAWNSTRING_LONGBOW), new Entry("arcanist_robe", 2, ModItems.ARCANIST_ROBE),
        new Entry("housecarl_warhorn", 3, ModItems.HOUSECARL_WARHORN), new Entry("oathkey", 4, ModItems.OATHKEY),
        new Entry("shadowreap_sickle", 5, ModItems.SHADOWREAP_SICKLE), new Entry("dawnbreaker", 5, ModItems.DAWNBREAKER),
        new Entry("hollow_crown", 5, ModItems.HOLLOW_CROWN), new Entry("everflame_lantern", 5, ModItems.EVERFLAME_LANTERN));

    private final InteractionHand hand;
    private int tab = TAB_PATH;
    private int left, top;
    private int storyChapter, storyPage;
    private int pathChapter;
    private String selected;
    private int listIndex;
    private int bookPage;
    private Set<String> done = new HashSet<>(), paid = new HashSet<>(), boons = new HashSet<>();
    private final List<Hit> hits = new ArrayList<>();
    private String pendingBoon;
    private int pendingTicks;

    private record Hit(int x, int y, int w, int h, Runnable action) {
        boolean in(double mx, double my) {
            return mx >= x && mx < x + w && my >= y && my < y + h;
        }
    }

    public ChronicleScreen(InteractionHand hand) {
        this(hand, -1);
    }

    public ChronicleScreen(InteractionHand hand, int openTab) {
        super(Component.translatable("item.oathbound.lantern_chronicle"));
        this.hand = hand;
        if (openTab >= 0) this.tab = openTab;
    }

    // ------------------------------------------------------------------ state
    private CompoundTag state() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return new CompoundTag();
        ItemStack book = mc.player.getItemInHand(hand);
        if (!book.is(ModItems.LANTERN_CHRONICLE.get())) {
            book = ItemStack.EMPTY;
            var inv = mc.player.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (inv.getItem(i).is(ModItems.LANTERN_CHRONICLE.get())) {
                    book = inv.getItem(i);
                    break;
                }
            }
        }
        return book.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
    }

    private static Set<String> set(String csv) {
        return csv.isEmpty() ? new HashSet<>() : new HashSet<>(Arrays.asList(csv.split(",")));
    }

    private void refresh() {
        CompoundTag t = state();
        done = set(t.getStringOr("done", ""));
        paid = set(t.getStringOr("paid", ""));
        boons = set(t.getStringOr("boons", ""));
        if (pendingBoon != null && (boons.contains(pendingBoon) || --pendingTicks <= 0)) pendingBoon = null;
    }

    private enum Status { LOCKED, ACTIVE, DONE, PAID }

    private Status status(Quest q) {
        if (paid.contains(q.id())) return Status.PAID;
        if (done.contains(q.id())) return Status.DONE;
        if (q.parent() == null || done.contains(q.parent())) return Status.ACTIVE;
        return Status.LOCKED;
    }

    private boolean chapterOpen(int chapter) {
        for (Quest q : QuestLog.QUESTS.values()) if (q.chapter() == chapter && status(q) != Status.LOCKED) return true;
        return chapter == 0;
    }

    private boolean chapterComplete(int chapter) {
        boolean any = false;
        for (Quest q : QuestLog.QUESTS.values()) {
            if (q.chapter() != chapter || !q.main()) continue;
            any = true;
            if (!done.contains(q.id())) return false;
        }
        return any;
    }

    private Quest nextMain() {
        for (Quest q : QuestLog.QUESTS.values()) if (q.main() && status(q) == Status.ACTIVE) return q;
        return null;
    }

    // ------------------------------------------------------------------ setup & input
    @Override
    protected void init() {
        left = (width - W) / 2;
        top = (height - H) / 2;
        refresh();
        Quest next = nextMain();
        if (next != null) {
            pathChapter = next.chapter();
            selected = next.id();
            storyChapter = next.chapter();
        } else {
            selected = "root";
        }
    }

    @Override
    public void tick() {
        refresh();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private void sound(boolean page) {
        Minecraft.getInstance().getSoundManager().play(SimpleSoundInstance.forUI(page ? SoundEvents.BOOK_PAGE_TURN : SoundEvents.UI_BUTTON_CLICK, page ? 1.0f : 1.3f));
    }

    @Override
    public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
        if (event.button() == 0) {
            for (int i = hits.size() - 1; i >= 0; i--) {
                if (hits.get(i).in(event.x(), event.y())) {
                    hits.get(i).action().run();
                    return true;
                }
            }
        }
        return super.mouseClicked(event, doubleClick);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double sx, double sy) {
        if (sy == 0) return false;
        int d = sy > 0 ? -1 : 1;
        switch (tab) {
            case TAB_STORY -> turnStory(d);
            case TAB_PATH -> {
                int c = Mth.clamp(pathChapter + d, 0, QuestLog.CHAPTERS - 1);
                if (c != pathChapter && chapterOpen(c)) {
                    pathChapter = c;
                    sound(true);
                }
            }
            case TAB_BESTIARY, TAB_ARMORY -> {
                listIndex = Mth.clamp(listIndex + d, 0, (tab == TAB_BESTIARY ? BEASTS : RELICS).size() - 1);
                bookPage = 0;
            }
            default -> {}
        }
        return true;
    }

    private void turnStory(int d) {
        int pages = storyPages().size();
        int np = storyPage + d;
        if (np >= 0 && np < pages) {
            storyPage = np;
            sound(true);
        } else if (d > 0 && storyChapter < QuestLog.CHAPTERS && chapterOpen(storyChapter + 1)) {
            storyChapter++;
            storyPage = 0;
            sound(true);
        } else if (d < 0 && storyChapter > 0) {
            storyChapter--;
            storyPage = Math.max(0, storyPages().size() - 1);
            sound(true);
        }
    }

    // ------------------------------------------------------------------ geometry
    private int lx() {
        return left + 16;
    }

    private int rx() {
        return left + W / 2 + 6;
    }

    private int py() {
        return top + 12;
    }

    // ------------------------------------------------------------------ rendering
    @Override
    public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float pt) {
        hits.clear();
        drawBook(g, mx, my);
        switch (tab) {
            case TAB_STORY -> drawStory(g, mx, my);
            case TAB_PATH -> drawPath(g, mx, my);
            case TAB_TITHES -> drawTithes(g, mx, my);
            case TAB_BESTIARY -> drawCodex(g, mx, my, BEASTS, "bestiary");
            default -> drawCodex(g, mx, my, RELICS, "armory");
        }
        super.extractRenderState(g, mx, my, pt);
    }

    private void drawBook(GuiGraphicsExtractor g, int mx, int my) {
        float time = (System.currentTimeMillis() % 1_000_000L) / 1000f;
        // shadow and leather cover
        g.fill(left - 6, top - 4, left + W + 10, top + H + 8, 0x66000000);
        g.fill(left - 8, top - 6, left + W + 8, top + H + 6, LEATHER_EDGE);
        g.fillGradient(left - 7, top - 5, left + W + 7, top + H + 5, LEATHER, LEATHER_DARK);
        // tooled gold border on the leather
        g.outline(left - 4, top - 2, W + 8, H + 4, GOLD_DIM);
        for (int[] c : new int[][]{{left - 5, top - 3}, {left + W + 2, top - 3}, {left - 5, top + H}, {left + W + 2, top + H}}) {
            g.fill(c[0], c[1], c[0] + 3, c[1] + 3, GOLD);
        }
        // pages
        drawPage(g, left + 8, top + 4, true);
        drawPage(g, left + W / 2, top + 4, false);
        // gutter
        g.fillGradient(left + W / 2 - 4, top + 4, left + W / 2 + 4, top + 4 + PAGE_H + 8, 0x00000000, 0x44000000);
        g.fill(left + W / 2 - 1, top + 4, left + W / 2 + 1, top + 4 + PAGE_H + 8, 0x55000000);
        // drifting embers in the margins
        long seed = 0x1D872B41L;
        for (int i = 0; i < 18; i++) {
            seed = seed * 6364136223846793005L + 1442695040888963407L;
            float bx = (seed >>> 40) % 12;
            float speed = 6 + (seed >>> 20) % 10;
            float y = (H + 10) - ((time * speed + (seed >>> 8) % 300) % (H + 12));
            int x = (i % 2 == 0 ? left - 7 : left + W) + (int) bx - 2 + (int) (Math.sin(time * 1.3 + i) * 1.5);
            int a = (int) (120 + 100 * Math.sin(time * 3 + i));
            g.fill(x, top + (int) y - 5, x + 1, top + (int) y - 4, (Mth.clamp(a, 20, 230) << 24) | 0xFFB45A);
        }
        // ribbons
        for (int i = 0; i < TAB_KEYS.length; i++) {
            int x = left + W + 6, y = top + 16 + i * 30;
            boolean on = tab == i;
            boolean hover = mx >= x && mx < x + 58 && my >= y && my < y + 22;
            int len = on ? 58 : hover ? 52 : 46;
            g.fill(x, y, x + len, y + 22, TAB_COLORS[i]);
            g.fill(x, y, x + len, y + 2, 0x33FFFFFF);
            g.fill(x + len - 6, y + 22, x + len, y + 26, TAB_COLORS[i]);
            g.text(font, Component.translatable("chronicle.oathbound.tab." + TAB_KEYS[i]), x + 5, y + 7, on ? GOLD_BRIGHT : 0xFFF3E6C6, true);
            final int t = i;
            hits.add(new Hit(x, y, 58, 22, () -> {
                if (tab != t) {
                    tab = t;
                    listIndex = 0;
                    bookPage = 0;
                    sound(true);
                }
            }));
        }
    }

    private void drawPage(GuiGraphicsExtractor g, int x, int y, boolean leftPage) {
        int w = PAGE_W + 8, h = PAGE_H + 8;
        g.fill(x - 1, y - 1, x + w + 1, y + h + 1, PAPER_EDGE);
        g.fillGradient(x, y, x + w, y + h, PAPER, PAPER_SHADE);
        // foxing and age at the outer edges
        int edge = leftPage ? x : x + w - 6;
        g.fillGradient(edge, y, edge + 6, y + h, 0x18553311, 0x28553311);
        // stacked page edges
        for (int i = 1; i <= 3; i++) {
            int ex = leftPage ? x - 1 - i : x + w + i;
            g.fill(ex, y + i, ex + 1, y + h - i, i % 2 == 0 ? PAPER_SHADE : PAPER_EDGE);
        }
    }

    private void heading(GuiGraphicsExtractor g, Component text, int x, int y, int width) {
        g.centeredText(font, text.copy().withStyle(ChatFormatting.BOLD), x + width / 2, y, RUBRIC);
        int w = Math.min(width - 10, font.width(text) + 24);
        int cx = x + width / 2;
        g.fill(cx - w / 2, y + 11, cx + w / 2, y + 12, GOLD_DIM);
        g.fill(cx - 2, y + 10, cx + 2, y + 13, RUBRIC);
    }

    private List<FormattedCharSequence> wrap(Component c, int width) {
        return font.split(c, width);
    }

    private int paragraph(GuiGraphicsExtractor g, Component c, int x, int y, int width, int color) {
        for (FormattedCharSequence line : wrap(c, width)) {
            g.text(font, line, x, y, color, false);
            y += font.lineHeight + 1;
        }
        return y;
    }

    private void arrows(GuiGraphicsExtractor g, int mx, int my, int x, int y, boolean prev, boolean next, Runnable back, Runnable fwd) {
        g.text(font, "◀", x, y, prev ? RUBRIC : INK_FAINT, false);
        g.text(font, "▶", x + 150, y, next ? RUBRIC : INK_FAINT, false);
        if (prev) hits.add(new Hit(x - 2, y - 2, 12, 12, back));
        if (next) hits.add(new Hit(x + 148, y - 2, 12, 12, fwd));
    }

    // ------------------------------------------------------------------ the Chronicle (story)
    private List<List<FormattedCharSequence>> storyPages() {
        Component text = chapterOpen(storyChapter)
            ? styled(Component.translatable(storyChapter >= QuestLog.CHAPTERS - 1 && done.contains("morvane") ? "chronicle.oathbound.lore.epilogue" : "chronicle.oathbound.lore." + storyChapter).getString())
            : Component.translatable("chronicle.oathbound.lore.sealed");
        List<FormattedCharSequence> lines = wrap(text, PAGE_W - 8);
        int per = (PAGE_H - 44) / (font.lineHeight + 1);
        List<List<FormattedCharSequence>> pages = new ArrayList<>();
        for (int i = 0; i < lines.size(); i += per) pages.add(lines.subList(i, Math.min(lines.size(), i + per)));
        if (pages.isEmpty()) pages.add(List.of());
        return pages;
    }

    /** Turns simple markup (*gold*, _rubric_) into real styles so colour survives wrapping. */
    static MutableComponent styled(String text) {
        MutableComponent out = Component.empty();
        Style style = Style.EMPTY;
        StringBuilder run = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            char ch = text.charAt(i);
            if (ch == '*' || ch == '_') {
                if (run.length() > 0) {
                    out.append(Component.literal(run.toString()).withStyle(style));
                    run.setLength(0);
                }
                Style target = ch == '*' ? Style.EMPTY.withColor(0xA0721C).withBold(true) : Style.EMPTY.withColor(0x8C2A2A).withItalic(true);
                style = style.equals(target) ? Style.EMPTY : target;
                continue;
            }
            run.append(ch);
        }
        if (run.length() > 0) out.append(Component.literal(run.toString()).withStyle(style));
        return out;
    }

    private void drawStory(GuiGraphicsExtractor g, int mx, int my) {
        int x = lx(), y = py();
        heading(g, Component.translatable("chronicle.oathbound.tab.story"), x, y, PAGE_W);
        y += 22;
        for (int c = 0; c <= QuestLog.CHAPTERS; c++) {
            boolean open = c < QuestLog.CHAPTERS ? chapterOpen(c) : done.contains("morvane");
            boolean sel = c == storyChapter;
            boolean hover = mx >= x && mx < x + PAGE_W && my >= y - 2 && my < y + 18;
            if (sel) g.fill(x - 2, y - 3, x + PAGE_W, y + 17, 0x33C9941E);
            else if (hover && open) g.fill(x - 2, y - 3, x + PAGE_W, y + 17, 0x18000000);
            String num = c < NUMERALS.length ? NUMERALS[c] : "†";
            g.text(font, num, x + 2, y + 4, open ? RUBRIC : INK_FAINT, false);
            Component title = open ? Component.translatable(c < QuestLog.CHAPTERS ? "chronicle.oathbound.chapter." + c : "chronicle.oathbound.chapter.epilogue")
                : Component.translatable("chronicle.oathbound.sealed");
            g.text(font, title, x + 22, y + 4, open ? INK : INK_FAINT, false);
            if (open && chapterComplete(c)) g.text(font, "✓", x + PAGE_W - 12, y + 4, C_DONE, false);
            final int cc = c;
            if (open) hits.add(new Hit(x - 2, y - 3, PAGE_W + 2, 20, () -> {
                storyChapter = cc;
                storyPage = 0;
                sound(true);
            }));
            y += 22;
        }
        // right page: the text
        int rx = rx(), ry = py();
        boolean epilogue = storyChapter >= QuestLog.CHAPTERS;
        heading(g, Component.translatable(epilogue ? "chronicle.oathbound.chapter.epilogue" : "chronicle.oathbound.chapter." + storyChapter), rx, ry, PAGE_W);
        List<List<FormattedCharSequence>> pages = storyPages();
        storyPage = Mth.clamp(storyPage, 0, pages.size() - 1);
        int ty = ry + 22;
        for (FormattedCharSequence line : pages.get(storyPage)) {
            g.text(font, line, rx + 2, ty, INK, false);
            ty += font.lineHeight + 1;
        }
        int ay = top + PAGE_H - 6;
        g.centeredText(font, Component.literal((storyPage + 1) + " / " + pages.size()), rx + PAGE_W / 2, ay, INK_SOFT);
        arrows(g, mx, my, rx + 4, ay, storyPage > 0 || storyChapter > 0, storyPage < pages.size() - 1 || (storyChapter < QuestLog.CHAPTERS && chapterOpen(storyChapter + 1)),
            () -> turnStory(-1), () -> turnStory(1));
    }

    // ------------------------------------------------------------------ the Path
    private void drawPath(GuiGraphicsExtractor g, int mx, int my) {
        int x = lx(), y = py();
        // chapter seals across the top
        for (int c = 0; c < QuestLog.CHAPTERS; c++) {
            int sx = x + c * 24, sy = y;
            boolean open = chapterOpen(c), sel = c == pathChapter;
            int ring = !open ? C_LOCKED : chapterComplete(c) ? C_DONE : C_ACTIVE;
            g.fill(sx, sy, sx + 20, sy + 16, sel ? ring : 0x22000000);
            g.outline(sx, sy, 20, 16, ring);
            g.centeredText(font, open ? NUMERALS[c] : "?", sx + 10, sy + 4, sel ? 0xFFFFFFFF : open ? INK : INK_FAINT);
            final int cc = c;
            if (open) hits.add(new Hit(sx, sy, 20, 16, () -> {
                pathChapter = cc;
                sound(true);
            }));
        }
        y += 22;
        g.text(font, Component.translatable("chronicle.oathbound.chapter." + pathChapter).withStyle(ChatFormatting.BOLD), x, y, RUBRIC, false);
        y += 14;
        // the path: main quests down the spine, side quests branching right
        List<Quest> mains = new ArrayList<>(), sides = new ArrayList<>();
        for (Quest q : QuestLog.QUESTS.values()) {
            if (q.chapter() != pathChapter) continue;
            (q.main() ? mains : sides).add(q);
        }
        Map<String, int[]> at = new HashMap<>();
        int spineX = x + 18;
        int step = Math.min(30, (PAGE_H - 70) / Math.max(1, mains.size()));
        for (int i = 0; i < mains.size(); i++) at.put(mains.get(i).id(), new int[]{spineX, y + i * step});
        int sideRow = 0;
        for (Quest q : sides) {
            int[] p = at.get(q.parent());
            int sx = spineX + 44 + (sideRow % 3) * 40;
            int sy = p != null ? p[1] + (sideRow % 2) * 10 : y + (sideRow / 3) * 28;
            if (pathChapter == QuestLog.CHAPTERS - 1) {
                sx = x + 8 + (sideRow % 4) * 40;
                sy = y + (sideRow / 4) * 34;
            }
            at.put(q.id(), new int[]{sx, sy});
            sideRow++;
        }
        float pulse = (float) (0.5 + 0.5 * Math.sin(System.currentTimeMillis() / 300.0));
        // connecting threads first
        for (Quest q : QuestLog.QUESTS.values()) {
            int[] p = at.get(q.id()), pp = q.parent() == null ? null : at.get(q.parent());
            if (p == null || pp == null) continue;
            int col = status(q) == Status.LOCKED ? 0x55A89070 : 0xAA8C6A2A;
            if (pp[0] == p[0]) g.fill(p[0] + 9, pp[1] + 20, p[0] + 11, p[1], col);
            else {
                g.fill(pp[0] + 20, pp[1] + 9, p[0], pp[1] + 11, col);
                g.fill(p[0] - 2, Math.min(pp[1] + 9, p[1] + 9), p[0], Math.max(pp[1] + 11, p[1] + 11), col);
            }
        }
        for (Quest q : QuestLog.QUESTS.values()) {
            int[] p = at.get(q.id());
            if (p == null) continue;
            Status s = status(q);
            int ring = switch (s) {
                case LOCKED -> C_LOCKED;
                case ACTIVE -> C_ACTIVE;
                case DONE -> C_OWED;
                case PAID -> C_DONE;
            };
            boolean sel = q.id().equals(selected);
            if (s == Status.ACTIVE) g.fill(p[0] - 2, p[1] - 2, p[0] + 22, p[1] + 22, ((int) (pulse * 90) << 24) | 0xE0A21E);
            g.fill(p[0], p[1], p[0] + 20, p[1] + 20, s == Status.LOCKED ? 0x22000000 : 0x55FFFFFF);
            g.outline(p[0], p[1], 20, 20, ring);
            if (sel) g.outline(p[0] - 1, p[1] - 1, 22, 22, RUBRIC);
            if (s == Status.LOCKED) g.centeredText(font, "?", p[0] + 10, p[1] + 6, INK_FAINT);
            else g.item(q.iconStack(), p[0] + 2, p[1] + 2);
            if (s == Status.PAID) g.text(font, "✓", p[0] + 14, p[1] + 12, C_DONE, true);
            else if (s == Status.DONE) g.text(font, "!", p[0] + 16, p[1] + 11, C_OWED, true);
            if (mx >= p[0] && mx < p[0] + 20 && my >= p[1] && my < p[1] + 20 && s != Status.LOCKED) {
                g.setTooltipForNextFrame(font, Component.translatable("quest.oathbound." + q.id() + ".title"), mx, my);
            }
            hits.add(new Hit(p[0], p[1], 20, 20, () -> {
                selected = q.id();
                sound(false);
            }));
        }
        drawQuestPage(g, mx, my);
    }

    private void drawQuestPage(GuiGraphicsExtractor g, int mx, int my) {
        int x = rx(), y = py();
        Quest next = nextMain();
        g.fill(x - 2, y - 2, x + PAGE_W, y + 26, 0x22C9941E);
        g.text(font, Component.translatable("chronicle.oathbound.next").withStyle(ChatFormatting.BOLD), x + 2, y, RUBRIC, false);
        Component nextText = next == null ? Component.translatable("chronicle.oathbound.next.none")
            : Component.translatable("quest.oathbound." + next.id() + ".title");
        g.text(font, font.plainSubstrByWidth(nextText.getString(), PAGE_W - 8), x + 2, y + 12, INK, false);
        y += 34;
        Quest q = QuestLog.QUESTS.get(selected);
        if (q == null) return;
        Status s = status(q);
        if (s == Status.LOCKED) {
            heading(g, Component.translatable("chronicle.oathbound.sealed"), x, y, PAGE_W);
            paragraph(g, Component.translatable("chronicle.oathbound.locked_quest"), x + 2, y + 22, PAGE_W - 6, INK_SOFT);
            return;
        }
        heading(g, Component.translatable("quest.oathbound." + q.id() + ".title"), x, y, PAGE_W);
        y += 20;
        Component statusText = switch (s) {
            case ACTIVE -> Component.translatable("chronicle.oathbound.status.active").withStyle(ChatFormatting.GOLD);
            case DONE -> Component.translatable("chronicle.oathbound.status.owed").withStyle(ChatFormatting.DARK_RED);
            case PAID -> Component.translatable("chronicle.oathbound.status.paid").withStyle(ChatFormatting.DARK_GREEN);
            default -> Component.empty();
        };
        g.centeredText(font, statusText, x + PAGE_W / 2, y, 0xFFFFFFFF);
        y += 13;
        y = paragraph(g, Component.translatable("quest.oathbound." + q.id() + ".description"), x + 2, y, PAGE_W - 6, INK);
        y += 4;
        if (s == Status.ACTIVE) {
            y = paragraph(g, Component.literal("❧ ").append(Component.translatable("quest.oathbound." + q.id() + ".hint")).withStyle(ChatFormatting.ITALIC),
                x + 2, y, PAGE_W - 6, INK_SOFT);
            y += 4;
        }
        // the tithe
        int ty = Math.max(y, top + PAGE_H - 50);
        g.fill(x + 4, ty - 4, x + PAGE_W - 6, ty - 3, GOLD_DIM);
        g.text(font, Component.translatable("chronicle.oathbound.tithe").withStyle(ChatFormatting.BOLD), x + 2, ty, RUBRIC, false);
        int ix = x + 2;
        for (QuestLog.Reward r : q.rewards()) {
            ItemStack st = r.stack();
            g.item(st, ix, ty + 11);
            g.itemDecorations(font, st, ix, ty + 11);
            if (mx >= ix && mx < ix + 16 && my >= ty + 11 && my < ty + 27) g.setTooltipForNextFrame(font, st, mx, my);
            ix += 20;
        }
        if (q.xp() > 0) g.text(font, Component.translatable("chronicle.oathbound.xp", q.xp()), ix + 2, ty + 15, 0xFF4E8A2C, false);
        if (s == Status.DONE) {
            g.text(font, Component.translatable("chronicle.oathbound.collect").withStyle(ChatFormatting.ITALIC), x + 2, ty + 30, C_OWED, false);
        }
    }

    // ------------------------------------------------------------------ Tithes & Boons
    private void drawTithes(GuiGraphicsExtractor g, int mx, int my) {
        int x = lx(), y = py();
        heading(g, Component.translatable("chronicle.oathbound.tithes.title"), x, y, PAGE_W);
        y += 22;
        List<Quest> owed = new ArrayList<>();
        for (Quest q : QuestLog.QUESTS.values()) if (status(q) == Status.DONE) owed.add(q);
        y = paragraph(g, Component.translatable(owed.isEmpty() ? "chronicle.oathbound.tithes.none" : "chronicle.oathbound.tithes.owed", owed.size()), x, y, PAGE_W - 4, INK);
        y += 6;
        int ix = x, iy = y;
        for (Quest q : owed) {
            for (QuestLog.Reward r : q.rewards()) {
                ItemStack st = r.stack();
                g.fill(ix, iy, ix + 18, iy + 18, 0x22000000);
                g.item(st, ix + 1, iy + 1);
                g.itemDecorations(font, st, ix + 1, iy + 1);
                if (mx >= ix && mx < ix + 18 && my >= iy && my < iy + 18) g.setTooltipForNextFrame(font, st, mx, my);
                ix += 20;
                if (ix > x + PAGE_W - 20) {
                    ix = x;
                    iy += 20;
                }
            }
        }
        y = iy + 26;
        paragraph(g, Component.translatable("chronicle.oathbound.tithes.how").withStyle(ChatFormatting.ITALIC), x, Math.max(y, top + PAGE_H - 40), PAGE_W - 4, INK_SOFT);

        // Boons
        int rx = rx(), ry = py();
        heading(g, Component.translatable("chronicle.oathbound.boons.title"), rx, ry, PAGE_W);
        ry += 20;
        int choosing = -1;
        for (int c = 0; c < 6; c++) {
            String chosen = null;
            for (Boon b : QuestLog.BOONS) if (b.chapter() == c && boons.contains(b.id())) chosen = b.id();
            boolean complete = chapterComplete(c);
            Component line;
            int color;
            if (chosen != null) {
                line = Component.translatable("boon.oathbound." + chosen + ".title");
                color = C_DONE;
            } else if (complete) {
                line = Component.translatable("chronicle.oathbound.boons.choose");
                color = C_OWED;
                if (choosing < 0) choosing = c;
            } else {
                line = Component.translatable("chronicle.oathbound.boons.sealed");
                color = INK_FAINT;
            }
            g.text(font, NUMERALS[c], rx + 2, ry, RUBRIC, false);
            g.text(font, line, rx + 20, ry, color, false);
            ry += 11;
        }
        ry += 4;
        if (choosing >= 0) {
            g.text(font, Component.translatable("chronicle.oathbound.boons.prompt", NUMERALS[choosing]).withStyle(ChatFormatting.BOLD), rx + 2, ry, RUBRIC, false);
            ry += 12;
            for (Boon b : QuestLog.BOONS) {
                if (b.chapter() != choosing) continue;
                int cardH = 34;
                boolean hover = mx >= rx && mx < rx + PAGE_W - 4 && my >= ry && my < ry + cardH;
                g.fill(rx, ry, rx + PAGE_W - 4, ry + cardH, hover ? 0x44C9941E : 0x22000000);
                g.outline(rx, ry, PAGE_W - 4, cardH, hover ? GOLD : GOLD_DIM);
                g.item(new ItemStack(b.icon().get()), rx + 4, ry + 9);
                g.text(font, Component.translatable("boon.oathbound." + b.id() + ".title").withStyle(ChatFormatting.BOLD), rx + 24, ry + 3, INK, false);
                int ly = ry + 14;
                for (FormattedCharSequence l : wrap(Component.translatable("boon.oathbound." + b.id() + ".description"), PAGE_W - 34)) {
                    if (ly > ry + cardH - 8) break;
                    g.text(font, l, rx + 24, ly, INK_SOFT, false);
                    ly += 9;
                }
                boolean waiting = b.id().equals(pendingBoon);
                if (!waiting) hits.add(new Hit(rx, ry, PAGE_W - 4, cardH, () -> swear(b)));
                ry += cardH + 3;
            }
            g.text(font, Component.translatable("chronicle.oathbound.boons.once").withStyle(ChatFormatting.ITALIC), rx + 2, ry, INK_FAINT, false);
        } else {
            paragraph(g, Component.translatable("chronicle.oathbound.boons.about").withStyle(ChatFormatting.ITALIC), rx + 2, ry, PAGE_W - 6, INK_SOFT);
        }
    }

    private void swear(Boon b) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.getConnection() == null || pendingBoon != null) return;
        mc.getConnection().sendCommand("oathchronicle boon " + b.id());
        pendingBoon = b.id();
        pendingTicks = 60;
        sound(false);
    }

    // ------------------------------------------------------------------ Bestiary & Armory
    private void drawCodex(GuiGraphicsExtractor g, int mx, int my, List<Entry> entries, String kind) {
        int x = lx(), y = py();
        heading(g, Component.translatable("chronicle.oathbound.tab." + kind), x, y, PAGE_W);
        y += 20;
        listIndex = Mth.clamp(listIndex, 0, entries.size() - 1);
        for (int i = 0; i < entries.size(); i++) {
            Entry e = entries.get(i);
            boolean open = chapterOpen(e.chapter()) && (e.chapter() < 5 || done.contains("gloaming") || done.contains("morvane"));
            boolean sel = i == listIndex;
            if (sel) g.fill(x - 2, y - 1, x + PAGE_W, y + 16, 0x33C9941E);
            if (open) g.item(new ItemStack(e.icon().get()), x, y);
            else g.centeredText(font, "?", x + 8, y + 4, INK_FAINT);
            Component name = open ? Component.translatable(kind + ".oathbound." + e.id() + ".name") : Component.translatable("chronicle.oathbound.unknown");
            g.text(font, name, x + 20, y + 4, open ? INK : INK_FAINT, false);
            final int idx = i;
            hits.add(new Hit(x - 2, y - 1, PAGE_W + 2, 17, () -> {
                listIndex = idx;
                bookPage = 0;
                sound(false);
            }));
            y += 17;
        }
        Entry e = entries.get(listIndex);
        boolean open = chapterOpen(e.chapter()) && (e.chapter() < 5 || done.contains("gloaming") || done.contains("morvane"));
        int rx = rx(), ry = py();
        if (!open) {
            heading(g, Component.translatable("chronicle.oathbound.unknown"), rx, ry, PAGE_W);
            paragraph(g, Component.translatable("chronicle.oathbound.codex_locked"), rx + 2, ry + 24, PAGE_W - 6, INK_SOFT);
            return;
        }
        heading(g, Component.translatable(kind + ".oathbound." + e.id() + ".name"), rx, ry, PAGE_W);
        ry += 20;
        // a framed plate with the icon, drawn large
        g.fill(rx + PAGE_W / 2 - 22, ry, rx + PAGE_W / 2 + 22, ry + 44, 0x22000000);
        g.outline(rx + PAGE_W / 2 - 22, ry, 44, 44, GOLD_DIM);
        g.pose().pushMatrix();
        g.pose().translate(rx + PAGE_W / 2f - 16, ry + 6);
        g.pose().scale(2f, 2f);
        g.item(new ItemStack(e.icon().get()), 0, 0);
        g.pose().popMatrix();
        ry += 50;
        ry = paragraph(g, styled(Component.translatable(kind + ".oathbound." + e.id() + ".text").getString()), rx + 2, ry, PAGE_W - 6, INK);
        ry += 4;
        paragraph(g, Component.literal("❧ ").append(Component.translatable(kind + ".oathbound." + e.id() + ".note")).withStyle(ChatFormatting.ITALIC),
            rx + 2, ry, PAGE_W - 6, RUBRIC);
    }
}
