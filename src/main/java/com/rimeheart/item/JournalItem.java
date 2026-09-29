package com.rimeheart.item;

import com.rimeheart.quest.QuestLog;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * The Warden's Journal: opens the journal screen (story, field guide and quest log). While it sits in a
 * player's inventory the server keeps the player's quest progress mirrored onto it for the screen.
 */
public class JournalItem extends Item {
    public JournalItem(Properties props) {
        super(props);
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (level.isClientSide()) {
            com.rimeheart.client.ClientHooks.openJournal(hand);
        } else if (player instanceof ServerPlayer sp) {
            QuestLog.sync(sp, player.getItemInHand(hand));
        }
        player.playSound(SoundEvents.BOOK_PAGE_TURN, 1.0f, 1.0f);
        return InteractionResult.SUCCESS;
    }

    @Override
    public void inventoryTick(ItemStack stack, ServerLevel level, Entity entity, EquipmentSlot slot) {
        if (entity instanceof ServerPlayer player && player.tickCount % 20 == 0) {
            QuestLog.sync(player, stack);
        }
    }
}
