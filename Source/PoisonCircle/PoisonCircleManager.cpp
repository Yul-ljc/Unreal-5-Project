#include "PoisonCircleManager.h"

#include "DrawDebugHelpers.h"
#include "Engine/DamageEvents.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetMaterialLibrary.h"

APoisonCircleManager::APoisonCircleManager()
{
	PrimaryActorTick.bCanEverTick = true;

	AffectedPawnClass = APawn::StaticClass();
	CurrentCenter = FVector(InitialCenter.X, InitialCenter.Y, 0.0f);
	CurrentRadius = InitialRadius;

	FPoisonCircleShrinkEvent FirstShrink;
	FirstShrink.StartRadius = 0.0f;
	FirstShrink.EndRadius = 4000.0f;
	FirstShrink.TargetCenter = FVector2D(1720.0f, 3160.0f);
	FirstShrink.DelayBeforeShrink = 90.0f;
	FirstShrink.ShrinkDuration = 30.0f;

	FPoisonCircleShrinkEvent SecondShrink;
	SecondShrink.StartRadius = 0.0f;
	SecondShrink.EndRadius = 2800.0f;
	SecondShrink.TargetCenter = FVector2D(0.0f, 2000.0f);
	SecondShrink.DelayBeforeShrink = 60.0f;
	SecondShrink.ShrinkDuration = 20.0f;

	ShrinkEvents.Add(FirstShrink);
	ShrinkEvents.Add(SecondShrink);
}

void APoisonCircleManager::BeginPlay()
{
	Super::BeginPlay();

	CurrentCenter = FVector(InitialCenter.X, InitialCenter.Y, 0.0f);
	CurrentRadius = InitialRadius;

	if (bStartOnBeginPlay)
	{
		StartRound();
	}
}

void APoisonCircleManager::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	if (!bRoundActive)
	{
		return;
	}

	AdvanceShrink(DeltaSeconds);

	DamageElapsedTime += DeltaSeconds;
	if (DamageElapsedTime >= DamageInterval)
	{
		DamageElapsedTime = 0.0f;
		ApplyOutsideCircleDamage();
	}

	if (bDrawDebugCircle)
	{
		DrawCurrentCircle();
	}

	if (bDrawDebugTargetCircle)
	{
		DrawTargetCircle();
	}

	UpdateVisualParameters();
}

void APoisonCircleManager::StartRound()
{
	bRoundActive = true;
	CurrentCenter = FVector(InitialCenter.X, InitialCenter.Y, 0.0f);
	CurrentRadius = InitialRadius;
	CurrentEventIndex = ShrinkEvents.Num() > 0 ? 0 : INDEX_NONE;
	EventElapsedTime = 0.0f;
	DamageElapsedTime = 0.0f;
	PrepareCurrentEvent();
}

void APoisonCircleManager::StopRound()
{
	bRoundActive = false;
	CurrentEventIndex = INDEX_NONE;
	EventElapsedTime = 0.0f;
	DamageElapsedTime = 0.0f;
}

bool APoisonCircleManager::IsLocationInsideSafeCircle(FVector Location) const
{
	const FVector2D CircleCenter2D(CurrentCenter.X, CurrentCenter.Y);
	const FVector2D Location2D(Location.X, Location.Y);
	return FVector2D::Distance(CircleCenter2D, Location2D) <= CurrentRadius;
}

bool APoisonCircleManager::IsActorOutsideSafeCircle(const AActor* Actor) const
{
	return IsValid(Actor) && !IsLocationInsideSafeCircle(Actor->GetActorLocation());
}

void APoisonCircleManager::AdvanceShrink(float DeltaSeconds)
{
	if (!ShrinkEvents.IsValidIndex(CurrentEventIndex))
	{
		return;
	}

	const FPoisonCircleShrinkEvent& Event = ShrinkEvents[CurrentEventIndex];
	EventElapsedTime += DeltaSeconds;

	if (EventElapsedTime < Event.DelayBeforeShrink)
	{
		return;
	}

	const float ShrinkTime = EventElapsedTime - Event.DelayBeforeShrink;
	const float Alpha = FMath::Clamp(ShrinkTime / FMath::Max(Event.ShrinkDuration, 0.1f), 0.0f, 1.0f);

	CurrentRadius = FMath::Lerp(EventStartRadius, Event.EndRadius, Alpha);
	CurrentCenter = FMath::Lerp(EventStartCenter, FVector(Event.TargetCenter.X, Event.TargetCenter.Y, 0.0f), Alpha);

	if (Alpha >= 1.0f)
	{
		const bool bWasLastEvent = (CurrentEventIndex + 1 >= ShrinkEvents.Num());

		CurrentEventIndex++;
		EventElapsedTime = 0.0f;
		PrepareCurrentEvent();

		if (bWasLastEvent)
		{
			OnAllShrinkEventsComplete();
		}
	}
}

void APoisonCircleManager::OnAllShrinkEventsComplete()
{
	if (!ActorToSpawnOnComplete)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	World->SpawnActor<AActor>(ActorToSpawnOnComplete, SpawnLocationOnComplete, FRotator::ZeroRotator, SpawnParams);
}

void APoisonCircleManager::ApplyOutsideCircleDamage()
{
	UWorld* World = GetWorld();
	if (!World || !AffectedPawnClass)
	{
		return;
	}

	TArray<AActor*> Pawns;
	UGameplayStatics::GetAllActorsOfClass(World, AffectedPawnClass, Pawns);

	const float DamageAmount = DamagePerSecond * DamageInterval;
	for (AActor* PawnActor : Pawns)
	{
		if (!IsActorOutsideSafeCircle(PawnActor))
		{
			continue;
		}

		UGameplayStatics::ApplyDamage(PawnActor, DamageAmount, nullptr, this, DamageTypeClass);
	}
}

void APoisonCircleManager::DrawCurrentCircle() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FVector DrawCenter(CurrentCenter.X, CurrentCenter.Y, GetActorLocation().Z + DebugCircleHeightOffset);
	DrawDebugCircle(
		World,
		DrawCenter,
		CurrentRadius,
		DebugSegments,
		SafeZoneColor,
		false,
		0.0f,
		0,
		DebugLineThickness,
		FVector::ForwardVector,
		FVector::RightVector,
		false);
}

void APoisonCircleManager::DrawTargetCircle() const
{
	if (!ShrinkEvents.IsValidIndex(CurrentEventIndex))
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FPoisonCircleShrinkEvent& Event = ShrinkEvents[CurrentEventIndex];
	const FVector DrawCenter(Event.TargetCenter.X, Event.TargetCenter.Y, GetActorLocation().Z + DebugCircleHeightOffset);
	DrawDebugCircle(
		World,
		DrawCenter,
		Event.EndRadius,
		DebugSegments,
		TargetZoneColor,
		false,
		0.0f,
		0,
		DebugLineThickness * 0.5f,
		FVector::ForwardVector,
		FVector::RightVector,
		false);
}

void APoisonCircleManager::PrepareCurrentEvent()
{
	if (!ShrinkEvents.IsValidIndex(CurrentEventIndex))
	{
		return;
	}

	EventStartRadius = CurrentRadius;
	EventStartCenter = CurrentCenter;
}

void APoisonCircleManager::UpdateVisualParameters()
{
	if (!VisualParameterCollection)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	UKismetMaterialLibrary::SetScalarParameterValue(World, VisualParameterCollection, RadiusParameterName, CurrentRadius);
	UKismetMaterialLibrary::SetScalarParameterValue(World, VisualParameterCollection, FName("EdgeSoftness"), EdgeTransitionWidth);

	const FLinearColor CenterAsColor(CurrentCenter.X, CurrentCenter.Y, 0.0f, 0.0f);
	UKismetMaterialLibrary::SetVectorParameterValue(World, VisualParameterCollection, CenterParameterName, CenterAsColor);
}
