package com.oathbound.item;

import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModSounds;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;

import java.util.function.Consumer;

/**
 * The Lantern Chronicle: the Order's living book. Opens the Chronicle screen (story, the Path of quests,
 * bestiary and armoury). While it is in a player's inventory the server mirrors their progress onto it.
 */
public class ChronicleItem extends Item {
    public ChronicleItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (level.isClientSide()) {
            com.oathbound.client.ClientHooks.openChronicle(hand);
        } else if (player instanceof ServerPlayer sp) {
            QuestLog.sync(sp, player.getItemInHand(hand));
        }
        player.playSound(ModSounds.CHRONICLE_PAGE.get(), 0.8f, 1.0f);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, EquipmentSlot slot) {
        if (entity instanceof ServerPlayer player && player.tickCount % 20 == 0) {
            QuestLog.sync(player, stack);
        }
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        return true;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        Inscriptions.add(out, getDescriptionId() + ".desc", 2);
    }
}
