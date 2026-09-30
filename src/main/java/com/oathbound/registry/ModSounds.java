package com.oathbound.registry;

import com.oathbound.Oathbound;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

import java.util.ArrayList;
import java.util.List;

public final class ModSounds {
    public static final DeferredRegister<SoundEvent> SOUNDS = DeferredRegister.create(ForgeRegistries.SOUND_EVENTS, Oathbound.MODID);
    public static final List<String> NAMES = new ArrayList<>();

    // --- lantern, chronicle, quests
    public static final RegistryObject<SoundEvent> LANTERN_IGNITE = reg("lantern_ignite");
    public static final RegistryObject<SoundEvent> LANTERN_SEEK = reg("lantern_seek");
    public static final RegistryObject<SoundEvent> CHRONICLE_PAGE = reg("chronicle_page");
    public static final RegistryObject<SoundEvent> QUEST_COMPLETE = reg("quest_complete");
    public static final RegistryObject<SoundEvent> WAYSHRINE_KINDLE = reg("wayshrine_kindle");
    // --- puzzles
    public static final RegistryObject<SoundEvent> BELL_0 = reg("bell_0");
    public static final RegistryObject<SoundEvent> BELL_1 = reg("bell_1");
    public static final RegistryObject<SoundEvent> BELL_2 = reg("bell_2");
    public static final RegistryObject<SoundEvent> BELL_3 = reg("bell_3");
    public static final RegistryObject<SoundEvent> BELL_WRONG = reg("bell_wrong");
    public static final RegistryObject<SoundEvent> PUZZLE_SOLVED = reg("puzzle_solved");
    public static final RegistryObject<SoundEvent> WARD_DISSOLVE = reg("ward_dissolve");
    public static final RegistryObject<SoundEvent> DIAL_TURN = reg("dial_turn");
    public static final RegistryObject<SoundEvent> TOMB_OPEN = reg("tomb_open");
    public static final RegistryObject<SoundEvent> LIAR_WAKES = reg("liar_wakes");
    public static final RegistryObject<SoundEvent> GATE_OPEN = reg("gate_open");
    public static final RegistryObject<SoundEvent> GATE_HUM = reg("gate_hum");
    // --- weapons
    public static final RegistryObject<SoundEvent> RIPOSTE = reg("riposte");
    public static final RegistryObject<SoundEvent> HALBERD_THRUST = reg("halberd_thrust");
    public static final RegistryObject<SoundEvent> ANCHOR_THROW = reg("anchor_throw");
    public static final RegistryObject<SoundEvent> ANCHOR_HIT = reg("anchor_hit");
    public static final RegistryObject<SoundEvent> ARCANE_CHAIN = reg("arcane_chain");
    public static final RegistryObject<SoundEvent> ARCANE_ORB = reg("arcane_orb");
    public static final RegistryObject<SoundEvent> ORB_REFLECT = reg("orb_reflect");
    public static final RegistryObject<SoundEvent> WARHORN = reg("warhorn");
    public static final RegistryObject<SoundEvent> DAWN_CHARGE = reg("dawn_charge");
    public static final RegistryObject<SoundEvent> DAWN_BURST = reg("dawn_burst");
    public static final RegistryObject<SoundEvent> SICKLE_REAP = reg("sickle_reap");
    public static final RegistryObject<SoundEvent> FLASK_SHATTER = reg("flask_shatter");
    public static final RegistryObject<SoundEvent> SUN_ARROW = reg("sun_arrow");
    public static final RegistryObject<SoundEvent> SUNMARK = reg("sunmark");
    // --- creatures
    public static final RegistryObject<SoundEvent> GLOAMLING_AMBIENT = reg("gloamling_ambient");
    public static final RegistryObject<SoundEvent> GLOAMLING_HURT = reg("gloamling_hurt");
    public static final RegistryObject<SoundEvent> GLOAMLING_DEATH = reg("gloamling_death");
    public static final RegistryObject<SoundEvent> FORSWORN_AMBIENT = reg("forsworn_ambient");
    public static final RegistryObject<SoundEvent> FORSWORN_COLLAPSE = reg("forsworn_collapse");
    public static final RegistryObject<SoundEvent> FORSWORN_RISE = reg("forsworn_rise");
    public static final RegistryObject<SoundEvent> WIGHT_AMBIENT = reg("wight_ambient");
    public static final RegistryObject<SoundEvent> WIGHT_HURT = reg("wight_hurt");
    public static final RegistryObject<SoundEvent> VEILHOUND_HOWL = reg("veilhound_howl");
    public static final RegistryObject<SoundEvent> VEILHOUND_GROWL = reg("veilhound_growl");
    public static final RegistryObject<SoundEvent> TOME_FLUTTER = reg("tome_flutter");
    public static final RegistryObject<SoundEvent> TOME_CAST = reg("tome_cast");
    public static final RegistryObject<SoundEvent> MOTH_FLUTTER = reg("moth_flutter");
    public static final RegistryObject<SoundEvent> HOUSECARL_RISE = reg("housecarl_rise");
    // --- bosses
    public static final RegistryObject<SoundEvent> CALDRIS_ROAR = reg("caldris_roar");
    public static final RegistryObject<SoundEvent> SHIELD_BLOCK = reg("shield_block");
    public static final RegistryObject<SoundEvent> SHIELD_CHARGE = reg("shield_charge");
    public static final RegistryObject<SoundEvent> UNDERTOW = reg("undertow");
    public static final RegistryObject<SoundEvent> VEYL_LAUGH = reg("veyl_laugh");
    public static final RegistryObject<SoundEvent> VEYL_BLINK = reg("veyl_blink");
    public static final RegistryObject<SoundEvent> VEYL_MIRROR = reg("veyl_mirror");
    public static final RegistryObject<SoundEvent> HRODGAR_ROAR = reg("hrodgar_roar");
    public static final RegistryObject<SoundEvent> FLAIL_SLAM = reg("flail_slam");
    public static final RegistryObject<SoundEvent> TETHER_SNAP = reg("tether_snap");
    public static final RegistryObject<SoundEvent> MORVANE_VOICE = reg("morvane_voice");
    public static final RegistryObject<SoundEvent> MORVANE_ROAR = reg("morvane_roar");
    public static final RegistryObject<SoundEvent> BLADE_CROWN = reg("blade_crown");
    public static final RegistryObject<SoundEvent> ECLIPSE_PILLAR = reg("eclipse_pillar");
    public static final RegistryObject<SoundEvent> LANTERN_SNUFF = reg("lantern_snuff");
    public static final RegistryObject<SoundEvent> LANTERN_RELIGHT = reg("lantern_relight");
    public static final RegistryObject<SoundEvent> UNVEILED = reg("unveiled");
    public static final RegistryObject<SoundEvent> CROWN_SHATTER = reg("crown_shatter");
    public static final RegistryObject<SoundEvent> BOSS_SLASH = reg("boss_slash");
    // --- music & ambience
    public static final RegistryObject<SoundEvent> THEME_KEEPER = reg("theme_keeper");
    public static final RegistryObject<SoundEvent> THEME_MORVANE = reg("theme_morvane");
    public static final RegistryObject<SoundEvent> GLOAMING_AMBIENT = reg("gloaming_ambient");
    public static final RegistryObject<SoundEvent> DISC_LANTERNGUARD_HYMN = reg("disc_lanternguard_hymn");
    public static final RegistryObject<SoundEvent> DISC_WAYSHRINE_NOCTURNE = reg("disc_wayshrine_nocturne");
    public static final RegistryObject<SoundEvent> DISC_CHAPEL_TIDES = reg("disc_chapel_tides");
    public static final RegistryObject<SoundEvent> DISC_CROWN_OF_ASH = reg("disc_crown_of_ash");
    public static final RegistryObject<SoundEvent> MUSIC_GLOAMING = reg("music_gloaming");
    public static final RegistryObject<SoundEvent> GLOAMING_MOOD = reg("gloaming_mood");

    private static RegistryObject<SoundEvent> reg(String name) {
        NAMES.add(name);
        return SOUNDS.register(name, () -> SoundEvent.createVariableRangeEvent(Identifier.fromNamespaceAndPath(Oathbound.MODID, name)));
    }

    public static SoundEvent bell(int tone) {
        return switch (tone & 3) {
            case 0 -> BELL_0.get();
            case 1 -> BELL_1.get();
            case 2 -> BELL_2.get();
            default -> BELL_3.get();
        };
    }

    private ModSounds() {}
}
