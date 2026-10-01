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

    /** Whether the local player's Chronicle lists a finished quest whose tithe is still unpaid. */
    public static boolean owesTithes() {
        var player = Minecraft.getInstance().player;
        if (player == null) return false;
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            var stack = inv.getItem(i);
            if (!stack.is(com.oathbound.registry.ModItems.LANTERN_CHRONICLE.get())) continue;
            var tag = stack.getOrDefault(net.minecraft.core.component.DataComponents.CUSTOM_DATA, net.minecraft.world.item.component.CustomData.EMPTY).copyTag();
            String done = tag.getStringOr("done", ""), paid = "," + tag.getStringOr("paid", "") + ",";
            if (done.isEmpty()) return false;
            for (String id : done.split(",")) if (!paid.contains("," + id + ",")) return true;
            return false;
        }
        return false;
    }
}
