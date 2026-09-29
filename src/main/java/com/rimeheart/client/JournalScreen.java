package com.rimeheart.client;

import com.rimeheart.quest.QuestLog;
import com.rimeheart.quest.QuestLog.Quest;
import com.rimeheart.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.input.MouseButtonEvent;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * The Warden's Journal screen: a frosted, silver-trimmed book with drifting snow and three tabs.
 * <ul>
 *   <li><b>Story</b>: the lore of the falling stars.</li>
 *   <li><b>Field Guide</b>: chapters from the first frost to the endgame, paged.</li>
 *   <li><b>Quests</b>: the quest line by chapter, with objectives, hints, rewards and a Claim button.</li>
 * </ul>
 * Quest state comes from the journal item's custom data, which the server keeps up to date.
 */
public class JournalScreen extends Screen {
    public static final int TAB_STORY = 0, TAB_GUIDE = 1, TAB_QUESTS = 2;
    private static final int W = 336, H = 214;

    // palette (ARGB)
    private static final int GOLD = 0xFFA9DDF5, GOLD_DIM = 0xFF4F7C9A, GOLD_BRIGHT = 0xFFE4F6FF;
    private static final int NIGHT_TOP = 0xFF16304A, NIGHT_BOTTOM = 0xFF070D18;
    private static final int PARCHMENT = 0xFFEEF4F8, PARCHMENT_EDGE = 0xFF8FAAC0, INK = 0xFF1B2733, INK_MUTED = 0xFF566A7C;
    private static final int PURPLE_INK = 0xFF174A80, LIGHT = 0xFFE6F0F8, LIGHT_MUTED = 0xFF8FA6BA;
    private static final int C_LOCKED = 0xFF8A8A8A, C_ACTIVE = 0xFF2F5C9E, C_READY = 0xFF1C7FA6, C_CLAIMED = 0xFF2E7D32;

    /** Field-guide chapters: lang keys guide.rimeheart.N.title / guide.rimeheart.N.text. */
    public static final int GUIDE_CHAPTERS = 9;

    private final InteractionHand hand;
    private int tab;
    private int left, top;
    private int storyPage, guideChapter, guidePage;
    private String selected;
    private float listScroll;
    private int listContentHeight;
    private Button claimButton;
    private String pendingClaim;
    private int pendingTicks;
    private final List<Row> rows = new ArrayList<>();

    private record Row(String quest, int chapter, int y, int h) {}

    public JournalScreen(InteractionHand hand, int tab) {
        super(Component.translatable("journal.rimeheart.title"));
        this.hand = hand;
        this.tab = tab;
    }

    // ------------------------------------------------------------------ state

    private CompoundTag state() {
        Minecraft mc = Minecraft.getInstance();
        if (mc.player == null) return new CompoundTag();
        ItemStack held = mc.player.getItemInHand(hand);
        if (!held.is(ModItems.WARDENS_JOURNAL.get())) {
            held = ItemStack.EMPTY;
            var inv = mc.player.getInventory();
            for (int i = 0; i < inv.getContainerSize(); i++) {
                if (inv.getItem(i).is(ModItems.WARDENS_JOURNAL.get())) {
                    held = inv.getItem(i);
                    break;
                }
            }
        }
        return held.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
    }

    private static Set<String> split(String s) {
        return s.isEmpty() ? new HashSet<>() : new HashSet<>(Arrays.asList(s.split(",")));
    }

    private enum Status { LOCKED, ACTIVE, READY, CLAIMED }

    private Set<String> done = new HashSet<>(), claimed = new HashSet<>();

    private void refreshState() {
        CompoundTag tag = state();
        done = split(tag.getStringOr("quests_done", ""));
        claimed = split(tag.getStringOr("quests_claimed", ""));
    }

    private Status status(Quest q) {
        if (claimed.contains(q.id())) return Status.CLAIMED;
        if (done.contains(q.id())) return Status.READY;
        if (q.parent() == null || done.contains(q.parent())) return Status.ACTIVE;
        return Status.LOCKED;
    }

    // ------------------------------------------------------------------ setup

    @Override
    protected void init() {
        left = (width - W) / 2;
        top = (height - H) / 2;
        refreshState();
        if (selected == null) selected = defaultSelection();
        claimButton = addRenderableWidget(Button.builder(Component.translatable("journal.rimeheart.claim"), b -> claim())
            .bounds(left + W - 12 - 96, top + H - 12 - 20, 96, 20).build());
        rebuildRows();
        updateButton();
    }

    private String defaultSelection() {
        String firstActive = null;
        for (Quest q : QuestLog.QUESTS.values()) {
            Status s = status(q);
            if (s == Status.READY) return q.id();
            if (s == Status.ACTIVE && firstActive == null) firstActive = q.id();
        }
        return firstActive != null ? firstActive : "root";
    }

    private void rebuildRows() {
        rows.clear();
        int y = 0;
        for (int ch = 0; ch < QuestLog.CHAPTERS.length; ch++) {
            rows.add(new Row(null, ch, y, 13));
            y += 13;
            for (Quest q : QuestLog.QUESTS.values()) {
                if (q.chapter() != ch) continue;
                rows.add(new Row(q.id(), ch, y, 20));
                y += 20;
            }
            y += 3;
        }
        listContentHeight = y;
    }

    private void updateButton() {
        Quest q = QuestLog.QUESTS.get(selected);
        boolean show = tab == TAB_QUESTS && q != null;
        claimButton.visible = show;
        if (!show) return;
        Status s = status(q);
        boolean waiting = selected.equals(pendingClaim);
        claimButton.active = s == Status.READY && !waiting;
        claimButton.setMessage(Component.translatable(s == Status.CLAIMED ? "journal.rimeheart.claimed" : "journal.rimeheart.claim"));
    }

    private void claim() {
        Quest q = QuestLog.QUESTS.get(selected);
        Minecraft mc = Minecraft.getInstance();
        if (q == null || status(q) != Status.READY || mc.getConnection() == null) return;
        mc.getConnection().sendCommand("rimejournal claim " + q.id());
        pendingClaim = q.id();
        pendingTicks = 60;
        updateButton();
    }

    @Override
    public void tick() {
        refreshState();
        if (pendingClaim != null && (claimed.contains(pendingClaim) || --pendingTicks <= 0)) pendingClaim = null;
        updateButton();
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    // ------------------------------------------------------------------ input

    private void click(boolean pageTurn) {
        Minecraft.getInstance().getSoundManager().play(pageTurn
            ? SimpleSoundInstance.forUI(SoundEvents.BOOK_PAGE_TURN, 1.0f)
            : SimpleSoundInstance.forUI(SoundEvents.UI_BUTTON_CLICK, 1.0f));
    }

    private static boolean in(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx < x + w && my >= y && my < y + h;
    }

    @Override
    public boolean mouseClicked(MouseButtonEvent event, boolean doubleClick) {
        double mx = event.x(), my = event.y();
        if (event.button() == 0) {
            for (int i = 0; i < 3; i++) {
                if (in(mx, my, tabX(i), top + 21, 82, 15) && tab != i) {
                    tab = i;
                    click(true);
                    updateButton();
                    return true;
                }
            }
            if (tab == TAB_QUESTS && in(mx, my, listX(), listTop(), listW(), listBottom() - listTop())) {
                for (Row r : rows) {
                    if (r.quest() == null) continue;
                    int ry = listTop() + r.y() - (int) listScroll;
                    if (my >= ry && my < ry + r.h()) {
                        if (!r.quest().equals(selected)) {
                            selected = r.quest();
                            click(false);
                            updateButton();
                        }
                        return true;
                    }
                }
            }
            if (tab == TAB_GUIDE && in(mx, my, left + 12, top + 42, 104, H - 54)) {
                int idx = (int) ((my - (top + 44)) / 14);
                if (idx >= 0 && idx < GUIDE_CHAPTERS && idx != guideChapter) {
                    guideChapter = idx;
                    guidePage = 0;
                    click(true);
                    return true;
                }
            }
            if (tab != TAB_QUESTS) {
                int[] arrows = arrowBoxes();
                if (in(mx, my, arrows[0], arrows[1], 14, 12)) {
                    turnPage(-1);
                    return true;
                }
                if (in(mx, my, arrows[2], arrows[1], 14, 12)) {
                    turnPage(1);
                    return true;
                }
            }
        }
        return super.mouseClicked(event, doubleClick);
    }

    @Override
    public boolean mouseScrolled(double mx, double my, double scrollX, double scrollY) {
        if (tab == TAB_QUESTS) {
            listScroll = clampScroll(listScroll - (float) scrollY * 14f);
            return true;
        }
        if (scrollY != 0) turnPage(scrollY > 0 ? -1 : 1);
        return true;
    }

    private void turnPage(int dir) {
        if (tab == TAB_STORY) {
            int n = pages(storyText(), textWidth(TAB_STORY)).size();
            int np = Math.max(0, Math.min(n - 1, storyPage + dir));
            if (np != storyPage) {
                storyPage = np;
                click(true);
            }
        } else if (tab == TAB_GUIDE) {
            int n = pages(guideText(guideChapter), textWidth(TAB_GUIDE)).size();
            int np = Math.max(0, Math.min(n - 1, guidePage + dir));
            if (np != guidePage) {
                guidePage = np;
                click(true);
            } else if (dir > 0 && guideChapter < GUIDE_CHAPTERS - 1) {
                guideChapter++;
                guidePage = 0;
                click(true);
            } else if (dir < 0 && guideChapter > 0) {
                guideChapter--;
                guidePage = pages(guideText(guideChapter), textWidth(TAB_GUIDE)).size() - 1;
                click(true);
            }
        }
    }

    private float clampScroll(float v) {
        int view = listBottom() - listTop();
        return Math.max(0, Math.min(Math.max(0, listContentHeight - view), v));
    }

    // ------------------------------------------------------------------ layout helpers

    private int tabX(int i) {
        return left + W / 2 - 126 + i * 84;
    }

    private int listX() {
        return left + 12;
    }

    private int listW() {
        return 132;
    }

    private int listTop() {
        return top + 60;
    }

    private int listBottom() {
        return top + H - 12;
    }

    private int textWidth(int t) {
        return t == TAB_STORY ? W - 24 - 20 : W - 12 - 124 - 12 - 16;
    }

    private int[] arrowBoxes() {
        int panelRight = left + W - 12;
        int y = top + H - 12 - 16;
        return new int[]{panelRight - 42, y, panelRight - 22};
    }

    private int linesPerPage() {
        return (H - 42 - 12 - 30) / (font.lineHeight + 1);
    }

    private Component storyText() {
        return Component.translatable("journal.rimeheart.story");
    }

    private Component guideText(int chapter) {
        return Component.translatable("guide.rimeheart." + chapter + ".text");
    }

    private String guideTitle(int chapter) {
        return Component.translatable("guide.rimeheart." + chapter + ".title").getString();
    }

    private List<List<FormattedCharSequence>> pages(Component text, int width) {
        List<FormattedCharSequence> lines = font.split(text, width);
        List<List<FormattedCharSequence>> pages = new ArrayList<>();
        int per = Math.max(1, linesPerPage());
        for (int i = 0; i < lines.size(); i += per) pages.add(lines.subList(i, Math.min(lines.size(), i + per)));
        if (pages.isEmpty()) pages.add(List.of());
        return pages;
    }

    // ------------------------------------------------------------------ rendering

    @Override
    public void extractRenderState(GuiGraphicsExtractor g, int mx, int my, float partialTick) {
        drawFrame(g, mx, my);
        switch (tab) {
            case TAB_STORY -> drawStory(g);
            case TAB_GUIDE -> drawGuide(g, mx, my);
            default -> drawQuests(g, mx, my);
        }
        super.extractRenderState(g, mx, my, partialTick);
    }

    private void drawFrame(GuiGraphicsExtractor g, int mx, int my) {
        // gold double border and a night-sky gradient
        g.fill(left - 3, top - 3, left + W + 3, top + H + 3, 0xFF05060F);
        g.fill(left - 2, top - 2, left + W + 2, top + H + 2, GOLD_DIM);
        g.fill(left - 1, top - 1, left + W + 1, top + H + 1, 0xFF05060F);
        g.fillGradient(left, top, left + W, top + H, NIGHT_TOP, NIGHT_BOTTOM);
        // drifting snow
        float t = (System.currentTimeMillis() % 1_000_000L) / 1000f;
        long seed = 0x5DEECE66DL;
        for (int i = 0; i < 80; i++) {
            seed = seed * 6364136223846793005L + 1442695040888963407L;
            float bx = (seed >>> 33) % (W - 6);
            seed = seed * 6364136223846793005L + 1442695040888963407L;
            float by = (seed >>> 33) % (H - 6);
            float speed = 6f + (i % 7) * 3f;
            int sy = top + 3 + (int) ((by + t * speed) % (H - 6));
            int sx = left + 3 + (int) ((bx + (float) Math.sin(t * 0.8f + i) * 4f + W) % (W - 6));
            int a = 90 + (i % 5) * 30;
            g.fill(sx, sy, sx + 1, sy + 1, (a << 24) | 0xFFFFFF);
            if (i % 9 == 0) {
                int dim = ((a / 2) << 24) | 0xDDEEFF;
                g.fill(sx - 1, sy, sx, sy + 1, dim);
                g.fill(sx + 1, sy, sx + 2, sy + 1, dim);
                g.fill(sx, sy - 1, sx + 1, sy, dim);
                g.fill(sx, sy + 1, sx + 1, sy + 2, dim);
            }
        }
        // corner ornaments
        for (int[] c : new int[][]{{left + 3, top + 3}, {left + W - 6, top + 3}, {left + 3, top + H - 6}, {left + W - 6, top + H - 6}}) {
            g.fill(c[0], c[1], c[0] + 3, c[1] + 3, GOLD);
        }
        // title
        Component title = Component.literal("❄ ").append(Component.translatable("journal.rimeheart.title")).append(" ❄").withStyle(ChatFormatting.BOLD);
        g.centeredText(font, title, left + W / 2, top + 7, GOLD_BRIGHT);
        // tabs
        String[] names = {"journal.rimeheart.tab.story", "journal.rimeheart.tab.guide", "journal.rimeheart.tab.quests"};
        for (int i = 0; i < 3; i++) {
            int x = tabX(i), y = top + 21;
            boolean active = tab == i, hover = in(mx, my, x, y, 82, 15);
            g.fill(x, y, x + 82, y + 15, active ? GOLD : GOLD_DIM);
            g.fill(x + 1, y + 1, x + 81, y + 15, active ? PARCHMENT : hover ? 0xFF22435F : 0xFF10233A);
            Component label = Component.translatable(names[i]);
            if (i == TAB_QUESTS) {
                long ready = QuestLog.QUESTS.values().stream().filter(q -> status(q) == Status.READY).count();
                if (ready > 0) label = Component.translatable(names[i]).append(Component.literal(" (" + ready + ")").withStyle(ChatFormatting.GOLD));
            }
            g.centeredText(font, label, x + 41, y + 4, active ? PURPLE_INK : LIGHT);
        }
        g.fill(left + 10, top + 36, left + W - 10, top + 37, GOLD_DIM);
    }

    private void parchment(GuiGraphicsExtractor g, int x1, int y1, int x2, int y2) {
        g.fill(x1 - 1, y1 - 1, x2 + 1, y2 + 1, PARCHMENT_EDGE);
        g.fillGradient(x1, y1, x2, y2, 0xFFF5F9FC, 0xFFDCE7EF);
    }

    private void pageFooter(GuiGraphicsExtractor g, int page, int count, int x1, int x2) {
        int[] a = arrowBoxes();
        g.text(font, Component.translatable("journal.rimeheart.page", page + 1, count), x1 + 8, a[1] + 2, INK_MUTED, false);
        g.text(font, "◀", a[0] + 3, a[1] + 2, page > 0 || (tab == TAB_GUIDE && guideChapter > 0) ? PURPLE_INK : 0xFFB9C8D4, false);
        g.text(font, "▶", a[2] + 3, a[1] + 2, page < count - 1 || (tab == TAB_GUIDE && guideChapter < GUIDE_CHAPTERS - 1) ? PURPLE_INK : 0xFFB9C8D4, false);
    }

    private void drawStory(GuiGraphicsExtractor g) {
        int x1 = left + 12, y1 = top + 42, x2 = left + W - 12, y2 = top + H - 12;
        parchment(g, x1, y1, x2, y2);
        var pages = pages(storyText(), textWidth(TAB_STORY));
        storyPage = Math.min(storyPage, pages.size() - 1);
        int y = y1 + 8;
        for (FormattedCharSequence line : pages.get(storyPage)) {
            g.text(font, line, x1 + 10, y, INK, false);
            y += font.lineHeight + 1;
        }
        pageFooter(g, storyPage, pages.size(), x1, x2);
    }

    private void drawGuide(GuiGraphicsExtractor g, int mx, int my) {
        int lx = left + 12, ly = top + 42;
        g.fill(lx, ly, lx + 112, top + H - 12, 0x66000000);
        for (int i = 0; i < GUIDE_CHAPTERS; i++) {
            int y = ly + 2 + i * 14;
            boolean sel = i == guideChapter, hover = in(mx, my, lx, y, 112, 14);
            if (sel) g.fill(lx + 1, y, lx + 111, y + 13, 0x5594CDEB);
            else if (hover) g.fill(lx + 1, y, lx + 111, y + 13, 0x22FFFFFF);
            String name = font.plainSubstrByWidth(guideTitle(i), 104);
            g.text(font, name, lx + 5, y + 3, sel ? GOLD_BRIGHT : LIGHT, true);
        }
        int x1 = left + 12 + 124, y1 = top + 42, x2 = left + W - 12, y2 = top + H - 12;
        parchment(g, x1, y1, x2, y2);
        var pages = pages(guideText(guideChapter), textWidth(TAB_GUIDE));
        guidePage = Math.min(guidePage, pages.size() - 1);
        int y = y1 + 8;
        for (FormattedCharSequence line : pages.get(guidePage)) {
            g.text(font, line, x1 + 8, y, INK, false);
            y += font.lineHeight + 1;
        }
        pageFooter(g, guidePage, pages.size(), x1, x2);
    }

    private void drawQuests(GuiGraphicsExtractor g, int mx, int my) {
        int lx = listX(), lw = listW();
        // progress header
        int total = QuestLog.QUESTS.size();
        int complete = (int) QuestLog.QUESTS.keySet().stream().filter(done::contains).count();
        g.fill(lx, top + 42, lx + lw, top + H - 12, 0x66000000);
        g.text(font, Component.translatable("journal.rimeheart.progress", complete, total), lx + 4, top + 45, LIGHT, true);
        int barY = top + 55, barW = lw - 8;
        g.fill(lx + 4, barY, lx + 4 + barW, barY + 3, 0xFF1B3550);
        g.fillGradient(lx + 4, barY, lx + 4 + barW * complete / Math.max(1, total), barY + 3, GOLD_BRIGHT, GOLD_DIM);

        // quest list
        listScroll = clampScroll(listScroll);
        float pulse = 0.5f + 0.5f * (float) Math.sin(System.currentTimeMillis() / 180.0);
        g.enableScissor(lx, listTop(), lx + lw, listBottom());
        for (Row r : rows) {
            int ry = listTop() + r.y() - (int) listScroll;
            if (ry + r.h() < listTop() || ry > listBottom()) continue;
            if (r.quest() == null) {
                g.text(font, Component.translatable("journal.rimeheart.chapter." + r.chapter()).withStyle(ChatFormatting.BOLD), lx + 4, ry + 3, GOLD, true);
                g.fill(lx + 4, ry + 12, lx + lw - 6, ry + 13, 0x664F7C9A);
                continue;
            }
            Quest q = QuestLog.QUESTS.get(r.quest());
            Status s = status(q);
            boolean sel = q.id().equals(selected);
            boolean hover = in(mx, my, lx, ry, lw, r.h()) && my >= listTop() && my < listBottom();
            if (sel) {
                g.fill(lx + 1, ry, lx + lw - 5, ry + r.h(), 0x5594CDEB);
                g.outline(lx + 1, ry, lw - 6, r.h(), GOLD);
            } else if (hover) {
                g.fill(lx + 1, ry, lx + lw - 5, ry + r.h(), 0x22FFFFFF);
            }
            if (s == Status.LOCKED) {
                g.fill(lx + 4, ry + 2, lx + 20, ry + 18, 0xFF1B3550);
                g.centeredText(font, "?", lx + 12, ry + 6, LIGHT_MUTED);
            } else {
                g.item(q.iconStack(), lx + 4, ry + 2);
            }
            String name = s == Status.LOCKED ? Component.translatable("journal.rimeheart.locked_title").getString()
                : Component.translatable("quest.rimeheart." + q.id() + ".title").getString();
            name = trim(name, lw - 42);
            int nameColor = switch (s) {
                case LOCKED -> 0xFF5D7488;
                case CLAIMED -> 0xFFA7D9A9;
                case READY -> GOLD_BRIGHT;
                default -> LIGHT;
            };
            g.text(font, name, lx + 23, ry + 6, nameColor, true);
            String mark = switch (s) {
                case CLAIMED -> "✔";
                case READY -> "!";
                case ACTIVE -> "•";
                default -> "";
            };
            int markColor = s == Status.CLAIMED ? 0xFF55DD66 : s == Status.READY ? ((int) (155 + 100 * pulse) << 24 | 0x7FE0FF) : LIGHT_MUTED;
            if (!mark.isEmpty()) g.text(font, mark, lx + lw - 14, ry + 6, markColor, true);
        }
        g.disableScissor();
        // scrollbar
        int view = listBottom() - listTop();
        if (listContentHeight > view) {
            int barH = Math.max(12, view * view / listContentHeight);
            int by = listTop() + (int) ((view - barH) * (listScroll / (listContentHeight - view)));
            g.fill(lx + lw - 3, listTop(), lx + lw - 1, listBottom(), 0x44FFFFFF);
            g.fill(lx + lw - 3, by, lx + lw - 1, by + barH, GOLD);
        }

        drawQuestDetail(g, mx, my);
    }

    private String trim(String s, int width) {
        if (font.width(s) <= width) return s;
        return font.plainSubstrByWidth(s, width - font.width("...")) + "...";
    }

    private void drawQuestDetail(GuiGraphicsExtractor g, int mx, int my) {
        Quest q = QuestLog.QUESTS.get(selected);
        if (q == null) return;
        Status s = status(q);
        int x1 = left + 12 + listW() + 8, y1 = top + 42, x2 = left + W - 12, y2 = top + H - 12;
        int tw = x2 - x1 - 16;
        parchment(g, x1, y1, x2, y2);
        boolean locked = s == Status.LOCKED;

        // big icon
        if (locked) {
            g.fill(x1 + 8, y1 + 8, x1 + 40, y1 + 40, 0xFFCFDCE6);
            g.pose().pushMatrix();
            g.pose().translate(x1 + 24, y1 + 17);
            g.pose().scale(2f, 2f);
            g.centeredText(font, "?", 0, 0, INK_MUTED);
            g.pose().popMatrix();
        } else {
            g.pose().pushMatrix();
            g.pose().translate(x1 + 8, y1 + 8);
            g.pose().scale(2f, 2f);
            g.item(q.iconStack(), 0, 0);
            g.pose().popMatrix();
        }
        Component title = locked ? Component.translatable("journal.rimeheart.locked_title")
            : Component.translatable("quest.rimeheart." + q.id() + ".title");
        List<FormattedCharSequence> titleLines = font.split(title.copy().withStyle(ChatFormatting.BOLD), x2 - x1 - 54);
        int ty = y1 + 10;
        for (FormattedCharSequence line : titleLines.subList(0, Math.min(2, titleLines.size()))) {
            g.text(font, line, x1 + 46, ty, PURPLE_INK, false);
            ty += font.lineHeight + 1;
        }
        g.text(font, Component.translatable("journal.rimeheart.chapter." + q.chapter()), x1 + 46, Math.max(ty + 1, y1 + 30), INK_MUTED, false);

        int y = y1 + 46;
        Component statusText = switch (s) {
            case LOCKED -> Component.translatable("journal.rimeheart.status.locked",
                Component.translatable("quest.rimeheart." + q.parent() + ".title"));
            case ACTIVE -> Component.translatable("journal.rimeheart.status.active");
            case READY -> Component.translatable("journal.rimeheart.status.ready");
            case CLAIMED -> Component.translatable("journal.rimeheart.status.claimed");
        };
        int statusColor = switch (s) {
            case LOCKED -> C_LOCKED;
            case ACTIVE -> C_ACTIVE;
            case READY -> C_READY;
            case CLAIMED -> C_CLAIMED;
        };
        for (FormattedCharSequence line : font.split(statusText, tw)) {
            g.text(font, line, x1 + 8, y, statusColor, false);
            y += font.lineHeight + 1;
        }
        y += 3;
        if (!locked) {
            for (FormattedCharSequence line : font.split(Component.translatable("quest.rimeheart." + q.id() + ".description").withStyle(ChatFormatting.BOLD), tw)) {
                g.text(font, line, x1 + 8, y, INK, false);
                y += font.lineHeight + 1;
            }
            y += 3;
            List<FormattedCharSequence> hint = font.split(Component.translatable("quest.rimeheart." + q.id() + ".hint").withStyle(ChatFormatting.ITALIC), tw);
            int maxHint = Math.max(0, (y2 - 58 - y) / (font.lineHeight + 1));
            for (int i = 0; i < Math.min(maxHint, hint.size()); i++) {
                g.text(font, hint.get(i), x1 + 8, y, INK_MUTED, false);
                y += font.lineHeight + 1;
            }
        }

        // rewards
        int ry = y2 - 52;
        g.fill(x1 + 6, ry - 3, x2 - 6, ry - 2, 0x664F7C9A);
        g.text(font, Component.translatable("journal.rimeheart.rewards").withStyle(ChatFormatting.BOLD), x1 + 8, ry + 1, INK, false);
        int ix = x1 + 8, iy = ry + 11;
        for (QuestLog.Reward r : q.rewards()) {
            ItemStack stack = r.stack();
            g.fill(ix - 1, iy - 1, ix + 17, iy + 17, 0x33000000);
            g.item(stack, ix, iy);
            g.itemDecorations(font, stack, ix, iy);
            if (in(mx, my, ix, iy, 16, 16)) g.setTooltipForNextFrame(font, stack, mx, my);
            ix += 20;
        }
        if (q.xp() > 0) g.text(font, Component.translatable("journal.rimeheart.xp", q.xp()), ix + 2, iy + 4, 0xFF3C8D2F, false);
        if (s == Status.CLAIMED) {
            g.text(font, "✔", x2 - 20, ry + 1, C_CLAIMED, false);
        }
    }
}
