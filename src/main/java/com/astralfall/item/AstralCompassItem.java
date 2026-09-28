package com.astralfall.item;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.registry.ModTags;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.GlobalPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.LodestoneTracker;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.phys.Vec3;

import java.util.Optional;
import java.util.function.Consumer;

/**
 * Right-click to locate the nearest Shattered Observatory: the needle locks on and a trail of stars
 * shows the way. Sneak + right-click to switch between Observatory, Fallen Vessel and Sky Shrine.
 */
public class AstralCompassItem extends Item {
    private static final String[] NAMES = {"observatory", "fallen_vessel", "sky_shrine"};

    public AstralCompassItem(Properties props) {
        super(props);
    }

    private static TagKey<Structure> tag(int mode) {
        return switch (mode) {
            case 1 -> ModTags.FALLEN_VESSEL;
            case 2 -> ModTags.SKY_SHRINE;
            default -> ModTags.OBSERVATORY;
        };
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        int mode = ItemUtil.getInt(stack, "mode") % 3;
        if (player.isShiftKeyDown()) {
            mode = (mode + 1) % 3;
            ItemUtil.setInt(stack, "mode", mode);
            stack.remove(DataComponents.LODESTONE_TRACKER);
            if (!level.isClientSide()) {
                player.sendOverlayMessage(Component.translatable("message.astralfall.compass.mode", Component.translatable("structure.astralfall." + NAMES[mode])).withStyle(ChatFormatting.AQUA));
            }
            return InteractionResult.SUCCESS;
        }
        if (player.getCooldowns().isOnCooldown(stack)) return InteractionResult.PASS;
        if (level instanceof ServerLevel server) {
            player.getCooldowns().addCooldown(stack, 40);
            BlockPos found = server.findNearestMapStructure(tag(mode), player.blockPosition(), 100, false);
            Component name = Component.translatable("structure.astralfall." + NAMES[mode]);
            if (found == null) {
                player.sendOverlayMessage(Component.translatable("message.astralfall.compass.none", name).withStyle(ChatFormatting.GRAY));
                return InteractionResult.SUCCESS;
            }
            stack.set(DataComponents.LODESTONE_TRACKER, new LodestoneTracker(Optional.of(GlobalPos.of(server.dimension(), found)), false));
            Vec3 from = player.getEyePosition();
            Vec3 dir = new Vec3(found.getX() + 0.5 - from.x, 0, found.getZ() + 0.5 - from.z);
            int dist = (int) Math.sqrt(dir.lengthSqr());
            dir = dir.normalize();
            for (int i = 2; i <= 24; i++) {
                Vec3 p = from.add(dir.scale(i)).add(0, Math.sin(i * 0.5) * 0.3 - 0.3, 0);
                server.sendParticles(player instanceof net.minecraft.server.level.ServerPlayer sp ? sp : null, ModParticles.STAR_SPARKLE.get(), true, true, p.x, p.y, p.z, 2, 0.05, 0.05, 0.05, 0.0);
            }
            String cardinal = cardinal(dir);
            player.sendOverlayMessage(Component.translatable("message.astralfall.compass.found", name, dist, cardinal).withStyle(ChatFormatting.AQUA));
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.STAR_CHIME.get(), SoundSource.PLAYERS, 1.0f, 1.3f);
        }
        return InteractionResult.SUCCESS;
    }

    private static String cardinal(Vec3 dir) {
        double angle = Math.toDegrees(Math.atan2(dir.x, -dir.z));
        if (angle < 0) angle += 360;
        String[] names = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"};
        return names[(int) Math.round(angle / 45.0) % 8];
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.astral_compass.desc", 2);
        int mode = ItemUtil.getInt(stack, "mode") % 3;
        out.accept(Component.translatable("message.astralfall.compass.mode", Component.translatable("structure.astralfall." + NAMES[mode])).withStyle(ChatFormatting.AQUA));
    }
}
