package com.oathbound.item;

import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/** A shard of solid light. Use it to refuel the emptiest Warden's Lantern you carry. */
public class LumeniteShardItem extends Item {
    public static final int FUEL = 120;

    public LumeniteShardItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        ItemStack best = ItemStack.EMPTY;
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.getItem() instanceof WardensLanternItem l && !l.isEverflame() && s.getDamageValue() > 0 && (best.isEmpty() || s.getDamageValue() > best.getDamageValue())) best = s;
        }
        if (best.isEmpty()) {
            if (!level.isClientSide()) player.sendOverlayMessage(Component.translatable("message.oathbound.shard.no_lantern").withStyle(ChatFormatting.GRAY));
            return InteractionResult.PASS;
        }
        if (level instanceof ServerLevel server) {
            ((WardensLanternItem) best.getItem()).refuel(best, FUEL);
            if (!player.hasInfiniteMaterials()) player.getItemInHand(hand).shrink(1);
            server.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.LANTERN_IGNITE.get(), SoundSource.PLAYERS, 0.9f, 1.2f);
            Vfx.burst(server, ModParticles.EMBER.get(), player.position().add(0, 1.2, 0), 16, 0.3, 0.05);
            int pct = (int) Math.round(100.0 * (best.getMaxDamage() - 1 - best.getDamageValue()) / (best.getMaxDamage() - 1));
            player.sendOverlayMessage(Component.translatable("message.oathbound.shard.refuel", pct).withStyle(ChatFormatting.GOLD));
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 2);
    }
}
