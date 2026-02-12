

@router.get("/csat-score", response_model=float)
async def csat_score(
    emp: emp_dependency,
    db: db_dependency,
    kpi: kpi_dependency
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("csat-score endpoint called")
    return kpi.get_csat_score()