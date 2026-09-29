package com.oathbound.client;

import com.oathbound.client.screen.ChronicleScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.world.InteractionHand;

/** Client-only entry points reached from common code (only ever invoked on the physical client). */
public final class ClientHooks {
    private ClientHooks() {}

    public static void openChronicle(InteractionHand hand) {
        Minecraft.getInstance().setScreenAndShow(new ChronicleScreen(hand));
    }
}
