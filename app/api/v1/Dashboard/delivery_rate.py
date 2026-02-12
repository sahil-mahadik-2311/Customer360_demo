@router.get("/delivery-rate", response_model=float)
async def delivery_rate(
    emp: emp_dependency,
    db: db_dependency,
    kpi: kpi_dependency
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("delivery-rate endpoint called")
    return kpi.get_delivery_rate()
