package com.astralfall.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.item.component.WrittenBookContent;

import java.util.ArrayList;
import java.util.List;

/**
 * The Astral Journal: a complete in-game guide. Page 1 is a clickable table of contents, page 2 a
 * quick start, followed by ten chapters from the first meteor to the endgame.
 */
public final class AstralJournal {
    /** Number of chapter pages (book pages 3..). Keep in sync with tools/lang_en.py. */
    public static final int CONTENT_PAGES = 29;
    private static final String[] CHAPTERS = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"};
    private static final int[] CHAPTER_PAGES = {3, 5, 8, 10, 13, 17, 21, 23, 28, 30};

    private AstralJournal() {}

    public static WrittenBookContent content() {
        List<Filterable<Component>> pages = new ArrayList<>();
        MutableComponent toc = Component.translatable("book.astralfall.journal.title").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD)
            .append(Component.literal("\n"))
            .append(Component.translatable("book.astralfall.journal.toc_hint").withStyle(ChatFormatting.GRAY))
            .append(Component.literal("\n\n"));
        for (int i = 0; i < CHAPTERS.length; i++) {
            final int page = CHAPTER_PAGES[i];
            toc.append(Component.translatable("book.astralfall.journal.chapter." + CHAPTERS[i])
                .withStyle(s -> s.withColor(ChatFormatting.DARK_BLUE).withUnderlined(true).withClickEvent(new ClickEvent.ChangePage(page))));
            toc.append(Component.literal("\n"));
        }
        pages.add(Filterable.passThrough(toc));
        pages.add(Filterable.passThrough(Component.translatable("book.astralfall.journal.quickstart")));
        for (int i = 1; i <= CONTENT_PAGES; i++) {
            pages.add(Filterable.passThrough(Component.translatable("book.astralfall.journal.page" + i)));
        }
        return new WrittenBookContent(Filterable.passThrough("Astral Journal"), "The Last Astronomer", 0, pages, true);
    }
}
