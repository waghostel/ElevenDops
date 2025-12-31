"""Demo data generator for Conversation Logs page.

This module provides realistic mock conversation data for demonstrating
the Conversation Logs page functionality. Data is based on real cataract
surgery post-operative care scenarios.
"""

from datetime import datetime, timedelta
from typing import List, Optional
import random

from streamlit_app.services.models import (
    ConversationSummary,
    ConversationDetail,
    ConversationMessage,
)


# Demo conversations simulating a patient's journey after cataract surgery
# Date range: 2025/06/01 - 2025/06/30 (one month post-op period)

DEMO_CONVERSATIONS = [
    {
        "id": "CONV_001",
        "date_offset": 1,  # June 1st - Day after surgery
        "duration": 180,
        "requires_attention": False,
        "main_concerns": ["Eye shield usage", "Drop schedule"],
        "answered_questions": [
            "How long should I wear the eye shield at night?",
            "What is the correct order for my eye drops?",
            "Can I take a shower tomorrow?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "Hi, I just had my cataract surgery yesterday. My vision is still a bit blurry - is this normal?", "offset_min": 0},
            {"role": "agent", "content": "Hello! Yes, this is completely normal. It's common for vision to be blurry for a few days after cataract surgery due to temporary corneal swelling. Most patients notice significant improvement within 24-48 hours. Make sure to keep using your prescribed eye drops and wear your protective eye shield when sleeping.", "offset_min": 1},
            {"role": "patient", "content": "Okay good. How long do I need to wear the eye shield?", "offset_min": 2},
            {"role": "agent", "content": "You should wear the protective plastic eye shield whenever you sleep, including naps, for the first week after surgery. This prevents accidental rubbing or pressure from your pillow while you sleep.", "offset_min": 3},
            {"role": "patient", "content": "And about the eye drops - I have three different bottles. Which one do I use first?", "offset_min": 4},
            {"role": "agent", "content": "Great question! When using multiple eye drops, always wait at least 5 minutes between different medications so they don't wash each other out. The typical order is: antibiotic drops first, then wait 5 minutes, then steroid drops, wait another 5 minutes, then NSAID drops if prescribed. Check your instruction sheet for your specific schedule.", "offset_min": 5},
            {"role": "patient", "content": "Can I shower tomorrow?", "offset_min": 6},
            {"role": "agent", "content": "Yes, you can shower starting the day after surgery. However, be very careful to keep water, soap, and shampoo out of your operated eye for the first seven days. Tilt your head back when washing your hair so water runs away from your eye.", "offset_min": 7},
        ],
    },
    {
        "id": "CONV_002",
        "date_offset": 3,  # June 3rd
        "duration": 240,
        "requires_attention": True,
        "main_concerns": ["Severe headache", "Eye pain"],
        "answered_questions": [
            "Is mild stinging from eye drops normal?",
        ],
        "unanswered_questions": [
            "I have a severe headache around my eye and feel nauseous - is this dangerous?",
        ],
        "messages": [
            {"role": "patient", "content": "The eye drops are stinging a lot when I put them in. Is that okay?", "offset_min": 0},
            {"role": "agent", "content": "Yes, mild stinging after applying eye drops is completely normal and usually passes within a few minutes. This is often a reaction to the preservatives in the drops rather than the medication itself. Some patients also notice a metallic taste as the drops drain through the tear duct into the throat.", "offset_min": 1},
            {"role": "patient", "content": "I also have a really bad headache around my eye and I'm feeling nauseous. Should I be worried?", "offset_min": 3},
            {"role": "agent", "content": "A severe headache centered around your operated eye accompanied by nausea can be a sign of elevated eye pressure, which requires immediate medical attention. Please contact your surgeon's office or go to the emergency room right away. This is considered an urgent situation that needs to be evaluated promptly.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_003",
        "date_offset": 5,  # June 5th
        "duration": 150,
        "requires_attention": False,
        "main_concerns": ["Activity restrictions", "Lifting"],
        "answered_questions": [
            "Can I pick up my grandchild?",
            "When can I start light exercise?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "My granddaughter wants me to pick her up. She's about 15 pounds. Is that okay?", "offset_min": 0},
            {"role": "agent", "content": "I understand how hard it is to say no to grandchildren! However, during the first week after surgery, you should avoid lifting anything heavier than 10-15 pounds. This is because heavy lifting can increase pressure in your eye and potentially affect the healing incision. After your one-week follow-up, you can gradually resume normal lifting.", "offset_min": 1},
            {"role": "patient", "content": "What about walking? I usually take morning walks.", "offset_min": 3},
            {"role": "agent", "content": "Light walking is actually encouraged and perfectly fine to do! Just avoid bending over with your head below your waist and any vigorous exercise for the first week. Wear sunglasses outdoors to protect your eye from wind and debris. After the first week, you can gradually return to more strenuous activities.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_004",
        "date_offset": 7,  # June 7th - One week post-op
        "duration": 200,
        "requires_attention": False,
        "main_concerns": ["Tapering steroid drops", "Dry eye symptoms"],
        "answered_questions": [
            "How do I reduce my steroid drops?",
            "My eye feels dry and scratchy - what can I do?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "I finished my antibiotic drops. Now my instructions say to reduce the steroid drops. How exactly do I do that?", "offset_min": 0},
            {"role": "agent", "content": "Great job completing the antibiotic course! For the steroid drops, you'll follow a tapering schedule. If you were using them 4 times a day during week 1, you'll now reduce to 3 times a day for week 2, then 2 times a day for week 3, and finally once a day for week 4. This gradual reduction prevents rebound inflammation.", "offset_min": 1},
            {"role": "patient", "content": "Also, my eye has been feeling really dry and scratchy. Is that from the surgery?", "offset_min": 3},
            {"role": "agent", "content": "Yes, dry eye and a 'scratchy' or 'sandy' feeling is very common after cataract surgery and usually improves over a few weeks. You can use preservative-free artificial tears as often as needed for comfort - many patients use them 4-6 times a day initially. If using artificial tears and other drops, wait 5 minutes between them.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_005",
        "date_offset": 10,  # June 10th
        "duration": 120,
        "requires_attention": False,
        "main_concerns": ["Driving", "Work return"],
        "answered_questions": [
            "When can I drive again?",
            "When can I return to work?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "My vision seems pretty clear now. Can I start driving?", "offset_min": 0},
            {"role": "agent", "content": "Most patients can resume driving within 24-48 hours after surgery, once their vision has stabilized and they feel comfortable. However, you should verify with your doctor at your follow-up appointment that your vision meets the legal requirements for driving. Avoid night driving until you're confident with your vision.", "offset_min": 1},
            {"role": "patient", "content": "I work at an office desk job. When can I go back?", "offset_min": 2},
            {"role": "agent", "content": "Most patients with desk jobs can return to work within 2-3 days after surgery, as long as your work doesn't involve heavy lifting or exposure to dust. Since you have an office job, you should be fine to return soon. Just remember to take breaks to rest your eyes and continue using your eye drops as scheduled.", "offset_min": 3},
        ],
    },
    {
        "id": "CONV_006",
        "date_offset": 12,  # June 12th
        "duration": 280,
        "requires_attention": True,
        "main_concerns": ["New floaters", "Light flashes"],
        "answered_questions": [],
        "unanswered_questions": [
            "I'm seeing lightning flashes and lots of new floaters - what should I do?",
        ],
        "messages": [
            {"role": "patient", "content": "Something strange is happening. I'm seeing flashing lights like lightning, and there are suddenly a lot of dark spots floating in my vision. Is this normal?", "offset_min": 0},
            {"role": "agent", "content": "This is an urgent situation. The sudden appearance of lightning-like flashes and a shower of new floaters or dark spots can be signs of a retinal tear or detachment. Please contact your surgeon's office immediately for an emergency dilated eye exam, or go to the emergency room if the office is closed. Time is important in diagnosing and treating retinal issues.", "offset_min": 1},
            {"role": "patient", "content": "Oh no, really? It just started about an hour ago.", "offset_min": 2},
            {"role": "agent", "content": "Yes, please seek immediate medical attention. Even if it turns out to be nothing serious, these symptoms must be evaluated urgently. A retinal tear, if present, can often be treated effectively if caught early. Do not wait - call your doctor now or go to the emergency room.", "offset_min": 3},
        ],
    },
    {
        "id": "CONV_007",
        "date_offset": 14,  # June 14th - Two weeks post-op
        "duration": 160,
        "requires_attention": False,
        "main_concerns": ["Swimming", "Makeup"],
        "answered_questions": [
            "Can I go swimming now?",
            "When can I wear eye makeup?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "It's been two weeks. Can I go swimming now? My grandkids have a pool party.", "offset_min": 0},
            {"role": "agent", "content": "Two weeks post-surgery is typically when swimming becomes safe! You can enjoy the pool with your grandkids. However, consider wearing swim goggles for extra protection and avoid submerging your head underwater if possible. Also, avoid hot tubs for a bit longer as they can harbor more bacteria.", "offset_min": 1},
            {"role": "patient", "content": "What about eye makeup? I have a wedding to attend next week.", "offset_min": 3},
            {"role": "agent", "content": "At two weeks post-surgery, you should be cleared to wear eye makeup again. Just make sure to use fresh makeup products - this is a good time to replace any old mascara or eyeliner to reduce infection risk. Be gentle when applying and removing makeup around your eye.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_008",
        "date_offset": 18,  # June 18th
        "duration": 190,
        "requires_attention": False,
        "main_concerns": ["Second eye surgery", "Lens options"],
        "answered_questions": [
            "When can I have surgery on my other eye?",
        ],
        "unanswered_questions": [
            "Should I get a premium multifocal lens or stick with the standard lens for my second eye?",
        ],
        "messages": [
            {"role": "patient", "content": "I'm really happy with how this eye is recovering! When can I have the cataract removed from my other eye?", "offset_min": 0},
            {"role": "agent", "content": "That's wonderful to hear! Doctors typically recommend waiting 1-2 weeks between cataract surgeries on each eye. This ensures the first eye is stable and healing well before proceeding. It also allows your surgeon to evaluate the outcome and make any adjustments to the lens power for your second eye if needed.", "offset_min": 1},
            {"role": "patient", "content": "I've heard about multifocal lenses that let you see near and far without glasses. Should I get that for my second eye?", "offset_min": 3},
            {"role": "agent", "content": "Premium multifocal or trifocal lenses can significantly reduce your dependence on glasses for both near and distance vision. However, the choice between standard monofocal lenses and premium lenses involves factors like your personal visual needs, lifestyle, and budget. This is an important decision that should be discussed in detail with your surgeon, who can explain the pros and cons specific to your situation.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_009",
        "date_offset": 21,  # June 21st
        "duration": 140,
        "requires_attention": False,
        "main_concerns": ["Color perception change"],
        "answered_questions": [
            "Why do colors look different now?",
            "Will my brain adjust to this?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "I've noticed colors look much brighter and more blue/white in my operated eye compared to my other eye. Is something wrong?", "offset_min": 0},
            {"role": "agent", "content": "Nothing is wrong at all! This is actually a very common observation after cataract surgery. Your cataract had been filtering out blue light and causing a yellowish tint to your vision over time. Now that the cloudy lens is replaced with a clear artificial lens, you're seeing colors more accurately. Whites appear brighter and blues more vivid.", "offset_min": 1},
            {"role": "patient", "content": "It's a bit disorienting having the two eyes see colors differently.", "offset_min": 2},
            {"role": "agent", "content": "That's understandable! Your brain will gradually adapt to this new input through a process called neuroadaptation. Within a few weeks, your brain will learn to process the difference between your two eyes, and the discrepancy will become much less noticeable. After your second eye surgery, both eyes will match again.", "offset_min": 3},
        ],
    },
    {
        "id": "CONV_010",
        "date_offset": 25,  # June 25th
        "duration": 170,
        "requires_attention": False,
        "main_concerns": ["Reading glasses", "Vision clarity"],
        "answered_questions": [
            "Why do I still need reading glasses?",
            "When will my prescription be stable?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "My distance vision is great now, but I still can't read without glasses. I thought the new lens would fix everything?", "offset_min": 0},
            {"role": "agent", "content": "I understand this can be confusing. The standard monofocal lens implanted during cataract surgery is typically set to focus at one distance - usually far/distance vision. This means most patients will still need reading glasses for close-up tasks like reading. This is normal and expected with standard lens implants.", "offset_min": 1},
            {"role": "patient", "content": "When can I get new reading glasses?", "offset_min": 3},
            {"role": "agent", "content": "Your vision typically stabilizes around 4-6 weeks after surgery. Your surgeon will check your vision at your one-month follow-up and can provide a prescription for glasses at that time if needed. Some patients find inexpensive over-the-counter readers work well for them.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_011",
        "date_offset": 28,  # June 28th
        "duration": 210,
        "requires_attention": False,
        "main_concerns": ["Lens longevity", "Future issues"],
        "answered_questions": [
            "How long will my artificial lens last?",
            "Can cataracts come back?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "My neighbor said she had to have another surgery years after her cataract surgery. Will I need that too? Do the lenses wear out?", "offset_min": 0},
            {"role": "agent", "content": "Your artificial intraocular lens is designed to last your entire lifetime and does not wear out or need to be replaced. It's made of stable, non-degradable materials. What your neighbor likely experienced is called Posterior Capsule Opacification (PCO), sometimes called a 'secondary cataract.'", "offset_min": 1},
            {"role": "patient", "content": "So cataracts can come back?", "offset_min": 3},
            {"role": "agent", "content": "No, once a cataract is removed, it cannot come back. However, about 20% of patients develop PCO where the thin membrane behind the lens becomes cloudy over months or years. If this happens, it's easily and permanently fixed with a quick, painless laser procedure done in the office that takes only a few minutes.", "offset_min": 4},
        ],
    },
    {
        "id": "CONV_012",
        "date_offset": 30,  # June 30th - One month post-op
        "duration": 130,
        "requires_attention": False,
        "main_concerns": ["Final recovery", "Activity clearance"],
        "answered_questions": [
            "Am I fully recovered now?",
            "Can I resume all activities?",
        ],
        "unanswered_questions": [],
        "messages": [
            {"role": "patient", "content": "It's been a month since my surgery. Am I fully healed now?", "offset_min": 0},
            {"role": "agent", "content": "Congratulations on reaching the one-month milestone! Most patients are considered fully healed at this point. Your corneal incision should be completely sealed, and any residual inflammation should have resolved. Your surgeon will confirm this at your follow-up appointment.", "offset_min": 1},
            {"role": "patient", "content": "So I can go back to doing everything - gym, swimming, all my normal activities?", "offset_min": 2},
            {"role": "agent", "content": "Yes! At one month post-surgery, you're typically cleared for all normal activities including gym workouts, swimming, hot tubs, and any other activities you enjoy. Just continue to protect your eyes from direct trauma and wear sunglasses outdoors. Enjoy your improved vision!", "offset_min": 3},
        ],
    },
]


def generate_demo_conversations(patient_id: str = "A123456789") -> List[ConversationSummary]:
    """Generate demo conversation summaries for the Conversation Logs page.
    
    Args:
        patient_id: The patient ID to use for demo data.
        
    Returns:
        List of ConversationSummary objects spanning June 2025.
    """
    base_date = datetime(2025, 6, 1, 9, 0, 0)  # Start June 1, 2025 at 9 AM
    summaries = []
    
    for conv in DEMO_CONVERSATIONS:
        conversation_date = base_date + timedelta(days=conv["date_offset"] - 1)
        # Add some time variation
        conversation_date = conversation_date.replace(
            hour=random.randint(8, 18),
            minute=random.randint(0, 59)
        )
        
        summaries.append(ConversationSummary(
            conversation_id=conv["id"],
            patient_id=patient_id,
            agent_id="AGENT_CATARACT_CARE",
            agent_name="Cataract Post-Op Care Assistant",
            requires_attention=conv["requires_attention"],
            main_concerns=conv["main_concerns"],
            total_messages=len(conv["messages"]),
            answered_count=len(conv["answered_questions"]),
            unanswered_count=len(conv["unanswered_questions"]),
            duration_seconds=conv["duration"],
            created_at=conversation_date,
        ))
    
    return summaries


def generate_demo_conversation_detail(
    conversation_id: str, 
    patient_id: str = "A123456789"
) -> Optional[ConversationDetail]:
    """Generate detailed conversation view for a specific conversation.
    
    Args:
        conversation_id: The conversation ID to get details for.
        patient_id: The patient ID to use.
        
    Returns:
        ConversationDetail object or None if not found.
    """
    base_date = datetime(2025, 6, 1, 9, 0, 0)
    
    for conv in DEMO_CONVERSATIONS:
        if conv["id"] == conversation_id:
            conversation_date = base_date + timedelta(days=conv["date_offset"] - 1)
            conversation_date = conversation_date.replace(hour=10, minute=30)
            
            # Generate message objects
            messages = []
            for msg in conv["messages"]:
                msg_time = conversation_date + timedelta(minutes=msg["offset_min"])
                messages.append(ConversationMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=msg_time,
                    audio_data=None,
                ))
            
            return ConversationDetail(
                conversation_id=conv["id"],
                patient_id=patient_id,
                agent_id="AGENT_CATARACT_CARE",
                agent_name="Cataract Post-Op Care Assistant",
                requires_attention=conv["requires_attention"],
                main_concerns=conv["main_concerns"],
                total_messages=len(conv["messages"]),
                answered_count=len(conv["answered_questions"]),
                unanswered_count=len(conv["unanswered_questions"]),
                duration_seconds=conv["duration"],
                created_at=conversation_date,
                messages=messages,
                answered_questions=conv["answered_questions"],
                unanswered_questions=conv["unanswered_questions"],
            )
    
    return None


def generate_demo_statistics(conversations: List[ConversationSummary]) -> dict:
    """Generate statistics from demo conversation data.
    
    Args:
        conversations: List of conversation summaries.
        
    Returns:
        Dictionary with conversation statistics.
    """
    if not conversations:
        return {
            "total_conversations": 0,
            "average_duration_seconds": 0,
            "average_duration_formatted": "0m 0s",
            "attention_percentage": 0.0,
        }
    
    total = len(conversations)
    total_duration = sum(c.duration_seconds for c in conversations)
    avg_duration = total_duration // total
    attention_count = sum(1 for c in conversations if c.requires_attention)
    
    minutes = avg_duration // 60
    seconds = avg_duration % 60
    
    return {
        "total_conversations": total,
        "average_duration_seconds": avg_duration,
        "average_duration_formatted": f"{minutes}m {seconds}s",
        "attention_percentage": (attention_count / total) * 100,
    }


def generate_demo_patient_summary() -> dict:
    """Generate aggregated patient summary across all demo conversations.
    
    Returns:
        Dictionary with:
        - answered_questions: List of all questions successfully answered by AI
        - unanswered_questions: List of questions that couldn't be fully answered
        - doctor_action_items: List of items requiring doctor confirmation/discussion
    """
    all_answered = []
    all_unanswered = []
    
    for conv in DEMO_CONVERSATIONS:
        all_answered.extend(conv["answered_questions"])
        all_unanswered.extend(conv["unanswered_questions"])
    
    # Doctor action items - derived from unanswered questions and attention-required conversations
    doctor_action_items = [
        "Discuss IOL options (monofocal vs multifocal) for second eye surgery",
        "Review patient's headache/nausea episode on June 3rd - check IOP history",
        "Follow up on floaters/flashes episode on June 12th - confirm retinal exam results",
        "Confirm patient is ready for second eye surgery scheduling",
    ]
    
    return {
        "answered_questions": all_answered,
        "unanswered_questions": all_unanswered,
        "doctor_action_items": doctor_action_items,
        "total_answered": len(all_answered),
        "total_unanswered": len(all_unanswered),
        "attention_episodes": sum(1 for c in DEMO_CONVERSATIONS if c["requires_attention"]),
    }
