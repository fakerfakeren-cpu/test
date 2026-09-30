package com.oathbound.item;

import com.oathbound.registry.ModSounds;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
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

/** A torn page of the Order's history. Read it (use) to hear what it says; the page is kept. */
public class LorePageItem extends Item {
    private final String page;
    private final int lines;

    public LorePageItem(Properties props, String page, int lines) {
        super(props);
        this.page = page;
        this.lines = lines;
    }

    @Override
    public InteractionResult use(Level level, Player player, InteractionHand hand) {
        if (!level.isClientSide()) {
            player.sendSystemMessage(Component.translatable("lore.oathbound." + page + ".title").withStyle(ChatFormatting.GOLD, ChatFormatting.BOLD));
            for (int i = 1; i <= lines; i++) {
                player.sendSystemMessage(Component.translatable("lore.oathbound." + page + "." + i).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            }
            level.playSound(null, player.getX(), player.getY(), player.getZ(), ModSounds.CHRONICLE_PAGE.get(), SoundSource.PLAYERS, 0.8f, 0.9f);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        out.accept(Component.translatable("lore.oathbound." + page + ".title").withStyle(ChatFormatting.GOLD));
        out.accept(Component.translatable("item.oathbound.lore_page.hint").withStyle(ChatFormatting.DARK_GRAY, ChatFormatting.ITALIC));
    }
}
