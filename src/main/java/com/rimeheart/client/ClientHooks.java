package com.rimeheart.client;

import net.minecraft.client.Minecraft;
import net.minecraft.world.InteractionHand;

/** Client-only entry points called from common code (only ever invoked on the physical client). */
public final class ClientHooks {
    private ClientHooks() {}

    public static void openJournal(InteractionHand hand) {
        Minecraft.getInstance().setScreenAndShow(new JournalScreen(hand, JournalScreen.TAB_QUESTS));
    }
}
