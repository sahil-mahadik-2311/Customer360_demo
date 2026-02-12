

@router.get("/avg-resolution-time", response_model=float)
async def avg_resolution_time(
    emp: emp_dependency,
    db: db_dependency,
    kpi: kpi_dependency
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("avg-resolution-time endpoint called")
    return kpi.get_avg_resolution_time()

