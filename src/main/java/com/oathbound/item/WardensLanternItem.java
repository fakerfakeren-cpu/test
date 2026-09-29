package com.oathbound.item;

import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.registry.ModWorldgen;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

import java.util.function.Consumer;

/**
 * The Warden's Lantern. Held in either hand it lights the way; carried anywhere it wards off Gloamrot; and
 * used, its flame leans towards the next place the Chronicle wants you to go ("Seek"). Its durability is its
 * fuel: refill it with Lumenite Shards or at any kindled Wayshrine. The Everflame Lantern never burns out.
 */
public class WardensLanternItem extends Item {
    private final boolean everflame;

    public WardensLanternItem(Properties props, boolean everflame) {
        super(props);
        this.everflame = everflame;
    }

    public boolean isEverflame() {
        return everflame;
    }

    public boolean isLit(ItemStack stack) {
        return everflame || !stack.isDamageableItem() || stack.getDamageValue() < stack.getMaxDamage() - 1;
    }

    /** Uses up fuel without ever breaking the lantern (it just goes dark). */
    public void burn(ItemStack stack, Player player, int amount) {
        if (everflame || !stack.isDamageableItem() || (player != null && player.hasInfiniteMaterials())) return;
        if (player instanceof ServerPlayer sp && QuestLog.hasBoon(sp, "lamplighters_thrift") && sp.getRandom().nextBoolean()) return;
        int before = stack.getDamageValue();
        int after = Math.min(stack.getMaxDamage() - 1, before + amount);
        stack.setDamageValue(after);
        if (player != null && before < stack.getMaxDamage() - 1 && after >= stack.getMaxDamage() - 1) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.lantern.out").withStyle(ChatFormatting.RED));
            player.level().playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.LANTERN_SNUFF.get(), SoundSource.PLAYERS, 0.8f, 1.2f);
        }
    }

    public void refuel(ItemStack stack, int amount) {
        if (everflame || !stack.isDamageableItem()) return;
        stack.setDamageValue(Math.max(0, stack.getDamageValue() - amount));
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server && player instanceof ServerPlayer sp) {
            if (!isLit(stack)) {
                player.sendOverlayMessage(Component.translatable("message.oathbound.lantern.empty").withStyle(ChatFormatting.RED));
                return InteractionResult.FAIL;
            }
            seek(server, sp, stack);
        }
        player.getCooldowns().addCooldown(stack, com.oathbound.event.GameEvents.cooldown(player, 60));
        return InteractionResult.SUCCESS;
    }

    private void seek(ServerLevel level, ServerPlayer player, ItemStack stack) {
        Vec3 eye = player.getEyePosition();
        BlockPos target = null;
        String label;
        if (level.dimension() == ModWorldgen.GLOAMING) {
            target = new BlockPos(0, player.getBlockY(), 0);
            label = "throne";
        } else {
            QuestLog.Destination dest = QuestLog.nextDestination(player);
            if (dest == null) {
                player.sendOverlayMessage(Component.translatable("message.oathbound.seek.none").withStyle(ChatFormatting.GOLD));
                level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.LANTERN_IGNITE.get(), SoundSource.PLAYERS, 0.6f, 1.4f);
                return;
            }
            label = dest.label();
            TagKey<Structure> tag = dest.structure();
            target = level.findNearestMapStructure(tag, player.blockPosition(), 64, false);
            if (target == null) {
                player.sendOverlayMessage(Component.translatable("message.oathbound.seek.far", Component.translatable("seek.oathbound." + label)).withStyle(ChatFormatting.GOLD));
                level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.LANTERN_SNUFF.get(), SoundSource.PLAYERS, 0.5f, 1.4f);
                return;
            }
        }
        burn(stack, player, 2);
        Vec3 to = Vec3.atCenterOf(target).subtract(eye);
        double dist = Math.sqrt(to.x * to.x + to.z * to.z);
        Vec3 dir = new Vec3(to.x, 0, to.z).normalize();
        // A ribbon of light that leans towards the goal and climbs a little, so it reads from first person.
        for (int i = 1; i <= 24; i++) {
            double t = i * 0.5;
            Vec3 p = eye.add(dir.scale(t)).add(0, -0.4 + Math.sin(i * 0.5) * 0.15 + t * 0.03, 0);
            level.sendParticles(player, i % 3 == 0 ? ModParticles.EMBER.get() : ModParticles.LUMEN_MOTE.get(), true, true, p.x, p.y, p.z, 1, 0.02, 0.02, 0.02, 0.0);
        }
        Vfx.burst(level, ModParticles.EMBER.get(), eye.add(dir.scale(0.8)).add(0, -0.3, 0), 8, 0.1, 0.03);
        level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.LANTERN_SEEK.get(), SoundSource.PLAYERS, 0.9f, 1.0f);
        float yaw = (float) (Mth.atan2(dir.z, dir.x) * (180 / Math.PI)) - 90f;
        String compass = compass(Mth.wrapDegrees(yaw + 180f));
        player.sendOverlayMessage(Component.translatable("message.oathbound.seek.found",
                Component.translatable("seek.oathbound." + label).withStyle(ChatFormatting.GOLD),
                Component.translatable("compass.oathbound." + compass),
                (int) dist)
            .withStyle(ChatFormatting.YELLOW));
    }

    /** 16-point compass name for a Minecraft yaw (0 = south). */
    static String compass(float yawFromNorth) {
        String[] names = {"n", "nne", "ne", "ene", "e", "ese", "se", "sse", "s", "ssw", "sw", "wsw", "w", "wnw", "nw", "nnw"};
        float deg = (yawFromNorth + 360f + 11.25f) % 360f;
        return names[(int) (deg / 22.5f) % 16];
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return everflame;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 3);
        if (!everflame && stack.isDamageableItem()) {
            int pct = (int) Math.round(100.0 * (stack.getMaxDamage() - 1 - stack.getDamageValue()) / (stack.getMaxDamage() - 1));
            out.accept(Component.translatable("item.oathbound.wardens_lantern.fuel", pct).withStyle(pct > 0 ? ChatFormatting.GOLD : ChatFormatting.RED));
        }
    }
}
