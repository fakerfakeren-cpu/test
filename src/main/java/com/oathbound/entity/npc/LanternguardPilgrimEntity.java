package com.oathbound.entity.npc;

import com.oathbound.entity.mob.FaunaEntity;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.npc.wanderingtrader.WanderingTrader;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.Level;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

/**
 * A pilgrim of the fallen Order, walking the old roads from wayshrine to wayshrine with a pack of its goods. It
 * sells the Order's metals, elixirs, torn pages and, rarely, a relic or a record; and it buys what the wilds give
 * up. It turns up where a wayshrine has been kindled, and now and then on the road, and moves on after a day.
 */
public class LanternguardPilgrimEntity extends WanderingTrader implements FaunaEntity {
    public LanternguardPilgrimEntity(EntityType<? extends LanternguardPilgrimEntity> type, Level level) {
        super(type, level);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return createMobAttributes().add(Attributes.MAX_HEALTH, 24.0).add(Attributes.MOVEMENT_SPEED, 0.5).add(Attributes.FOLLOW_RANGE, 48.0);
    }

    /** Lantern raised while someone is trading with it. */
    @Override
    public boolean fauna$action() {
        return isTrading();
    }

    private static MerchantOffer sell(int emeralds, Supplier<? extends ItemLike> what, int count, int uses) {
        return new MerchantOffer(new ItemCost(Items.EMERALD, emeralds), new ItemStack(what.get(), count), uses, 2, 0.05f);
    }

    private static MerchantOffer buy(Supplier<? extends ItemLike> what, int count, int emeralds, int uses) {
        return new MerchantOffer(new ItemCost(what.get(), count), new ItemStack(Items.EMERALD, emeralds), uses, 2, 0.05f);
    }

    @Override
    protected void updateTrades(ServerLevel level) {
        MerchantOffers offers = getOffers();
        RandomSource r = getRandom();
        // what every pilgrim carries
        offers.add(sell(1, ModItems.LUMENITE_SHARD, 3, 16));
        offers.add(sell(3, ModItems.LUMEN_FLASK, 2, 8));
        offers.add(sell(2, ModItems.HONEYED_MEAD, 2, 8));
        // and what this one happens to have
        List<MerchantOffer> pack = new ArrayList<>(List.of(
            sell(6, ModItems.TIDEBRONZE_BLEND, 2, 6), sell(8, ModItems.RUNESILVER_BLEND, 2, 6), sell(10, ModItems.GRAVEGOLD_BLEND, 2, 4),
            sell(5, ModItems.ELIXIR_OF_TIDES, 1, 4), sell(5, ModItems.ELIXIR_OF_WARDS, 1, 4), sell(5, ModItems.ELIXIR_OF_SHROUDS, 1, 4),
            sell(5, ModItems.ELIXIR_OF_THE_WAYFARER, 1, 4), sell(6, ModItems.ELIXIR_OF_VALOR, 1, 4), sell(3, ModItems.TRAIL_RATIONS, 3, 8),
            sell(2, ModItems.MOONPETAL_TEA, 1, 8), sell(8, ModBlocks.GLOAMWOOD_SAPLING, 2, 4), sell(4, ModBlocks.MOONPETAL, 3, 6),
            sell(12, ModItems.HUNTSMANS_HORN, 1, 1), sell(3, ModBlocks.GLIMMER_MOSS, 8, 6)));
        for (int i = 0; i < 5 && !pack.isEmpty(); i++) offers.add(pack.remove(r.nextInt(pack.size())));
        List<Supplier<? extends Item>> pages = List.of(ModItems.LORE_PAGE_FIRST_LANTERN, ModItems.LORE_PAGE_OATH_OF_EMBER, ModItems.LORE_PAGE_SUNDERING,
            ModItems.LORE_PAGE_LAST_WATCH, ModItems.LORE_PAGE_LUMENITE_RUSH, ModItems.LORE_PAGE_SUN_CULT, ModItems.LORE_PAGE_STAR_READERS);
        offers.add(sell(4, pages.get(r.nextInt(pages.size())), 1, 1));
        if (r.nextInt(3) == 0) {
            List<Supplier<? extends Item>> rare = List.of(ModItems.MUSIC_DISC_WAYSHRINE_NOCTURNE, ModItems.MUSIC_DISC_LANTERNGUARD_HYMN,
                ModItems.MUSIC_DISC_WILD_HUNT, ModItems.MUSIC_DISC_STARS_WENT_OUT, ModItems.BELL_OF_THE_DROWNED, ModItems.LANTERNGUARD_SIGNET);
            offers.add(sell(24, rare.get(r.nextInt(rare.size())), 1, 1));
        }
        // and what the wilds give up
        List<MerchantOffer> wants = new ArrayList<>(List.of(buy(ModItems.GLIMMER_ANTLER, 2, 3, 8), buy(ModItems.HAG_EYE, 2, 3, 6),
            buy(ModItems.EMBER_CORE, 1, 2, 8), buy(ModItems.RAW_VENISON, 6, 1, 12), buy(ModItems.BOAR_TUSK, 3, 2, 8),
            buy(ModItems.SHADOW_FANG, 1, 3, 6), buy(ModItems.MOSSBACK_SCUTE, 2, 2, 8), buy(ModItems.GLOAM_ESSENCE, 4, 2, 12)));
        for (int i = 0; i < 3 && !wants.isEmpty(); i++) offers.add(wants.remove(r.nextInt(wants.size())));
    }

    @Override
    public void aiStep() {
        super.aiStep();
        // a lantern-glow about its staff
        if (level().isClientSide() && random.nextInt(4) == 0) {
            float yaw = yBodyRot * net.minecraft.util.Mth.DEG_TO_RAD;
            level().addParticle(ModParticles.LUMEN_MOTE.get(), getX() - Math.cos(yaw) * 0.45, getY() + 2.05, getZ() - Math.sin(yaw) * 0.45, 0, 0.01, 0);
        }
    }

    /** Somewhere a pilgrim can stand, near {@code around}. */
    public static BlockPos standingNear(ServerLevel level, BlockPos around, RandomSource r, int min, int max) {
        for (int i = 0; i < 12; i++) {
            double a = r.nextDouble() * Math.PI * 2, d = min + r.nextDouble() * (max - min);
            int x = around.getX() + (int) Math.round(Math.cos(a) * d), z = around.getZ() + (int) Math.round(Math.sin(a) * d);
            int y = level.getHeight(net.minecraft.world.level.levelgen.Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, x, z);
            BlockPos p = new BlockPos(x, y, z);
            if (level.getBlockState(p.below()).isSolid() && level.isEmptyBlock(p) && level.isEmptyBlock(p.above())
                && level.getFluidState(p.below()).isEmpty() && Math.abs(y - around.getY()) < 12) return p;
        }
        return null;
    }
}
