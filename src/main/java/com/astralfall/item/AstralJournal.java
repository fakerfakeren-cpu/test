package com.astralfall.item;

import net.minecraft.network.chat.Component;
import net.minecraft.server.network.Filterable;
import net.minecraft.world.item.component.WrittenBookContent;

import java.util.ArrayList;
import java.util.List;

/** The in-game guide book: lore plus a walkthrough of the whole progression. */
public final class AstralJournal {
    public static final int PAGES = 10;

    private AstralJournal() {}

    public static WrittenBookContent content() {
        List<Filterable<Component>> pages = new ArrayList<>();
        for (int i = 1; i <= PAGES; i++) {
            pages.add(Filterable.passThrough(Component.translatable("book.astralfall.journal.page" + i)));
        }
        return new WrittenBookContent(Filterable.passThrough("Astral Journal"), "The Last Astronomer", 0, pages, true);
    }
}
