package com.astralfall.item;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.component.TooltipDisplay;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.HitResult;

import java.util.function.Consumer;

/** Mines a 3x3 area facing you. Sneak to mine a single block. */
public class StarmetalPickaxeItem extends Item {
    private static final ThreadLocal<Boolean> BUSY = ThreadLocal.withInitial(() -> false);

    public StarmetalPickaxeItem(Properties props) {
        super(props);
    }

    @Override
    public boolean mineBlock(ItemStack stack, Level level, BlockState state, BlockPos pos, LivingEntity miner) {
        boolean result = super.mineBlock(stack, level, state, pos, miner);
        if (level.isClientSide() || BUSY.get() || !(miner instanceof ServerPlayer player) || player.isShiftKeyDown()) return result;
        if (!stack.isCorrectToolForDrops(state)) return result;
        HitResult hit = player.pick(6.0, 0.0f, false);
        if (!(hit instanceof BlockHitResult bhr) || hit.getType() != HitResult.Type.BLOCK) return result;
        Direction face = bhr.getDirection();
        float centerHardness = state.getDestroySpeed(level, pos);
        BUSY.set(true);
        try {
            for (int a = -1; a <= 1; a++) {
                for (int b = -1; b <= 1; b++) {
                    if (a == 0 && b == 0) continue;
                    BlockPos p = switch (face.getAxis()) {
                        case X -> pos.offset(0, a, b);
                        case Y -> pos.offset(a, 0, b);
                        case Z -> pos.offset(a, b, 0);
                    };
                    BlockState s = level.getBlockState(p);
                    float h = s.getDestroySpeed(level, p);
                    if (s.isAir() || h < 0 || h > centerHardness + 1.5f || !stack.isCorrectToolForDrops(s)) continue;
                    if (stack.isEmpty()) break;
                    player.gameMode.destroyBlock(p);
                }
            }
        } finally {
            BUSY.set(false);
        }
        return result;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext ctx, TooltipDisplay display, Consumer<Component> out, TooltipFlag flag) {
        ItemUtil.tooltip(out, "item.astralfall.starmetal_pickaxe.desc", 2);
    }
}
