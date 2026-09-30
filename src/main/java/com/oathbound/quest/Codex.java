package com.oathbound.quest;

import com.oathbound.Oathbound;
import com.oathbound.registry.ModItems;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.stats.Stats;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;

/**
 * The Bestiary and Armory entries, and what each player has actually discovered: a creature once they have seen it
 * up close (or killed one), a relic once they have held it (or crafted or picked one up). Discoveries live in the
 * player's persisted data and are mirrored onto the Chronicle by {@link QuestLog#sync}.
 */
public final class Codex {
    public record Entry(String id, int chapter, Supplier<? extends Item> icon) {}

    public static final List<Entry> BEASTS = List.of(
        new Entry("lanternmoth", 0, ModItems.LANTERNMOTH_SPAWN_EGG), new Entry("gloamling", 0, ModItems.GLOAMLING_SPAWN_EGG),
        new Entry("sir_caldris", 1, ModItems.SIR_CALDRIS_SPAWN_EGG), new Entry("animated_tome", 2, ModItems.ANIMATED_TOME_SPAWN_EGG),
        new Entry("archmage_veyl", 2, ModItems.ARCHMAGE_VEYL_SPAWN_EGG), new Entry("barrow_wight", 3, ModItems.BARROW_WIGHT_SPAWN_EGG),
        new Entry("spectral_housecarl", 3, ModItems.SPECTRAL_HOUSECARL_SPAWN_EGG), new Entry("hrodgar", 3, ModItems.HRODGAR_SPAWN_EGG),
        new Entry("forsworn_knight", 4, ModItems.FORSWORN_KNIGHT_SPAWN_EGG), new Entry("veilhound", 5, ModItems.VEILHOUND_SPAWN_EGG),
        new Entry("morvane", 5, ModItems.MORVANE_SPAWN_EGG),
        new Entry("glimmerfawn", 0, ModItems.GLIMMERFAWN_SPAWN_EGG),
        new Entry("duskhare", 0, ModItems.DUSKHARE_SPAWN_EGG),
        new Entry("mossback_tortoise", 0, ModItems.MOSSBACK_TORTOISE_SPAWN_EGG),
        new Entry("lumen_beetle", 0, ModItems.LUMEN_BEETLE_SPAWN_EGG),
        new Entry("tidewader", 0, ModItems.TIDEWADER_SPAWN_EGG),
        new Entry("thornback_boar", 0, ModItems.THORNBACK_BOAR_SPAWN_EGG),
        new Entry("stonewarden", 0, ModItems.STONEWARDEN_SPAWN_EGG),
        new Entry("runewisp", 2, ModItems.RUNEWISP_SPAWN_EGG),
        new Entry("drowned_choirmonk", 1, ModItems.DROWNED_CHOIRMONK_SPAWN_EGG),
        new Entry("mire_hag", 3, ModItems.MIRE_HAG_SPAWN_EGG),
        new Entry("grave_crawler", 3, ModItems.GRAVE_CRAWLER_SPAWN_EGG),
        new Entry("gloam_stalker", 5, ModItems.GLOAM_STALKER_SPAWN_EGG),
        new Entry("shade_wraith", 5, ModItems.SHADE_WRAITH_SPAWN_EGG),
        new Entry("lumenite_mite", 0, ModItems.LUMENITE_MITE_SPAWN_EGG),
        new Entry("ashen_revenant", 4, ModItems.ASHEN_REVENANT_SPAWN_EGG),
        new Entry("elderhorn", 1, ModItems.ELDERHORN_SPAWN_EGG),
        new Entry("bog_mother", 2, ModItems.BOG_MOTHER_SPAWN_EGG),
        new Entry("cinder_colossus", 3, ModItems.CINDER_COLOSSUS_SPAWN_EGG),
        new Entry("glimmerstag", 0, ModItems.GLIMMERSTAG_SPAWN_EGG),
        new Entry("lanternguard_pilgrim", 0, ModItems.LANTERNGUARD_PILGRIM_SPAWN_EGG));

    public static final List<Entry> RELICS = List.of(
        new Entry("wardens_lantern", 0, ModItems.WARDENS_LANTERN), new Entry("oathsteel_longsword", 0, ModItems.OATHSTEEL_LONGSWORD),
        new Entry("wardens_halberd", 0, ModItems.WARDENS_HALBERD), new Entry("lumen_flask", 0, ModItems.LUMEN_FLASK),
        new Entry("drowned_anchor", 1, ModItems.DROWNED_ANCHOR), new Entry("staff_of_veyl", 2, ModItems.STAFF_OF_VEYL),
        new Entry("dawnstring_longbow", 2, ModItems.DAWNSTRING_LONGBOW), new Entry("arcanist_robe", 2, ModItems.ARCANIST_ROBE),
        new Entry("housecarl_warhorn", 3, ModItems.HOUSECARL_WARHORN), new Entry("oathkey", 4, ModItems.OATHKEY),
        new Entry("shadowreap_sickle", 5, ModItems.SHADOWREAP_SICKLE), new Entry("dawnbreaker", 5, ModItems.DAWNBREAKER),
        new Entry("hollow_crown", 5, ModItems.HOLLOW_CROWN), new Entry("everflame_lantern", 5, ModItems.EVERFLAME_LANTERN),
        new Entry("tidebronze_gladius", 1, ModItems.TIDEBRONZE_GLADIUS), new Entry("runesilver_rapier", 2, ModItems.RUNESILVER_RAPIER),
        new Entry("gravegold_khopesh", 3, ModItems.GRAVEGOLD_KHOPESH), new Entry("duskiron_glaive", 5, ModItems.DUSKIRON_GLAIVE),
        new Entry("dawnsteel_greatsword", 5, ModItems.DAWNSTEEL_GREATSWORD),
        new Entry("huntsmans_horn", 0, ModItems.HUNTSMANS_HORN), new Entry("bell_of_the_drowned", 1, ModItems.BELL_OF_THE_DROWNED),
        new Entry("grove_kings_crown", 1, ModItems.GROVE_KINGS_CROWN), new Entry("veyls_mirror", 2, ModItems.VEYLS_MIRROR),
        new Entry("bog_mothers_lantern", 2, ModItems.BOG_MOTHERS_LANTERN), new Entry("barrow_censer", 3, ModItems.BARROW_CENSER),
        new Entry("cinder_heart", 3, ModItems.CINDER_HEART), new Entry("lanternguard_signet", 4, ModItems.LANTERNGUARD_SIGNET),
        new Entry("heart_of_the_gloam", 5, ModItems.HEART_OF_THE_GLOAM), new Entry("sunshard_talisman", 5, ModItems.SUNSHARD_TALISMAN));

    private static final String KEY = "oathbound_codex";
    private static final double SIGHT = 20;

    private Codex() {}

    public static Set<String> discovered(ServerPlayer player) {
        String csv = player.getPersistentData().getCompoundOrEmpty("PlayerPersisted").getStringOr(KEY, "");
        return csv.isEmpty() ? new LinkedHashSet<>() : new LinkedHashSet<>(Arrays.asList(csv.split(",")));
    }

    public static String csv(ServerPlayer player) {
        return String.join(",", discovered(player));
    }

    /** Looks around and through the pack for anything new; cheap enough to run every couple of seconds. */
    public static void discover(ServerPlayer player) {
        Set<String> known = discovered(player);
        int before = known.size();
        // creatures in plain sight
        for (LivingEntity e : player.level().getEntitiesOfClass(LivingEntity.class, player.getBoundingBox().inflate(SIGHT),
            e -> e != player && e.isAlive())) {
            Identifier id = ForgeRegistries.ENTITY_TYPES.getKey(e.getType());
            if (id == null || !Oathbound.MODID.equals(id.getNamespace()) || known.contains(id.getPath())) continue;
            if (isBeast(id.getPath()) && player.hasLineOfSight(e)) known.add(id.getPath());
        }
        // relics in the pack
        var inv = player.getInventory();
        for (int i = 0; i < inv.getContainerSize(); i++) {
            ItemStack s = inv.getItem(i);
            if (s.isEmpty()) continue;
            Identifier id = ForgeRegistries.ITEMS.getKey(s.getItem());
            if (id != null && Oathbound.MODID.equals(id.getNamespace()) && isRelic(id.getPath())) known.add(id.getPath());
        }
        // and anything the player's own records already prove (kills, crafts, pickups)
        var stats = player.getStats();
        for (Entry b : BEASTS) {
            if (known.contains(b.id())) continue;
            EntityType<?> type = ForgeRegistries.ENTITY_TYPES.getValue(Identifier.fromNamespaceAndPath(Oathbound.MODID, b.id()));
            if (type != null && (stats.getValue(Stats.ENTITY_KILLED.get(type)) > 0 || stats.getValue(Stats.ENTITY_KILLED_BY.get(type)) > 0)) known.add(b.id());
        }
        for (Entry r : RELICS) {
            if (known.contains(r.id())) continue;
            Item item = r.icon().get();
            if (stats.getValue(Stats.ITEM_CRAFTED.get(item)) > 0 || stats.getValue(Stats.ITEM_PICKED_UP.get(item)) > 0) known.add(r.id());
        }
        if (known.size() == before) return;
        CompoundTag root = player.getPersistentData();
        CompoundTag persisted = root.getCompoundOrEmpty("PlayerPersisted");
        persisted.putString(KEY, String.join(",", known));
        root.put("PlayerPersisted", persisted);
        QuestLog.syncAll(player);
    }

    private static boolean isBeast(String id) {
        for (Entry e : BEASTS) if (e.id().equals(id)) return true;
        return false;
    }

    private static boolean isRelic(String id) {
        for (Entry e : RELICS) if (e.id().equals(id)) return true;
        return false;
    }
}
