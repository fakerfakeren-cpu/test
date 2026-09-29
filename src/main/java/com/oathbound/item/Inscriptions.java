package com.oathbound.item;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.monster.Enemy;
import net.minecraft.world.entity.player.Player;

import java.util.function.Consumer;

/** Tooltip text and small shared judgements used by Oathbound items. */
public final class Inscriptions {
    private Inscriptions() {}

    /**
     * Appends {@code key.1 .. key.n}. The first line is the flavour quote (italic, grey); the rest describe what the
     * item does (gold bullet points).
     */
    public static void add(Consumer<Component> out, String key, int lines) {
        for (int i = 1; i <= lines; i++) {
            if (i == 1) {
                out.accept(Component.translatable(key + "." + i).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            } else {
                out.accept(Component.literal(" • ").withStyle(ChatFormatting.GOLD)
                    .append(Component.translatable(key + "." + i).withStyle(ChatFormatting.YELLOW)));
            }
        }
    }

    /** Whether {@code e} is fair game for a player's area attack (monsters, or anything hunting that player). */
    public static boolean isFoeOf(Entity e, Player player) {
        if (e instanceof Enemy) return true;
        return e instanceof Mob m && m.getTarget() == player;
    }
}
