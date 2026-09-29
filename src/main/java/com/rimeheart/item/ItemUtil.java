package com.rimeheart.item;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

public final class ItemUtil {
    private ItemUtil() {}

    public static int getInt(ItemStack stack, String key) {
        CustomData data = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY);
        return data.copyTag().getIntOr(key, 0);
    }

    public static void setInt(ItemStack stack, String key, int value) {
        CompoundTag tag = stack.getOrDefault(DataComponents.CUSTOM_DATA, CustomData.EMPTY).copyTag();
        tag.putInt(key, value);
        stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));
    }

    /** Point the player is looking at, up to {@code range} blocks (block hit, or the end of the ray). */
    public static Vec3 lookTarget(Player player, double range) {
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getLookAngle().scale(range));
        BlockHitResult hit = player.level().clip(new ClipContext(eye, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player));
        return hit.getType() == HitResult.Type.MISS ? end : hit.getLocation();
    }

    public static boolean lookHitsBlock(Player player, double range) {
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getLookAngle().scale(range));
        return player.level().clip(new ClipContext(eye, end, ClipContext.Block.OUTLINE, ClipContext.Fluid.NONE, player)).getType() != HitResult.Type.MISS;
    }

    public static void tooltip(Consumer<Component> out, String key, int lines) {
        for (int i = 1; i <= lines; i++) {
            out.accept(Component.translatable(key + "." + i).withStyle(i == 1 ? net.minecraft.ChatFormatting.GRAY : net.minecraft.ChatFormatting.DARK_AQUA));
        }
    }

    public static boolean isHostileTo(Entity e, Player player) {
        return e instanceof net.minecraft.world.entity.monster.Enemy || (e instanceof net.minecraft.world.entity.Mob m && m.getTarget() == player);
    }
}
